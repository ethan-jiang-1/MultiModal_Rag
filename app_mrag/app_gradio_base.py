import time
import sys
import gradio as gr
import threading
import os
import html
import logging 
import re
import urllib.parse

if "./" not in sys.path:
    sys.path.append("./")

os.environ["GRADIO_USE_LOCAL_FONTS"] = "True"

from app_mrag._app_base import CUSTOM_CSS, QUESTION_LIST
from app_mrag._app_qa_core import main_loop_gradio, get_main_ret
from app_mrag._app_log_monitor import ProgressLogger
from md2vdb.utils.util_logging import setup_logger_handlers
from md2vdb.utils.util_git import get_git_version
from md2vdb.utils.util_model import get_gpt_model

def _process_markdown_images(markdown_str):
    """
    处理 Markdown 中的图片引用，解码 URL 编码的图片路径。
    
    :param markdown_str: 输入的 Markdown 字符串
    :return: 处理后的 Markdown 字符串
    """
    # 正则表达式匹配 Markdown 图片引用语法 ![alt text](image_url)
    image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'

    def decode_image_url(match):
        # 获取图片的 alt 文本和 URL
        alt_text = match.group(1)
        image_url = match.group(2)
        
        # 解码 URL 编码的部分
        decoded_url = urllib.parse.unquote(image_url)
        
        # 返回解码后的图片引用
        return f"![{alt_text}]({decoded_url})"
    
    # 使用 re.sub 替换匹配的图片引用为解码后的形式
    processed_markdown = re.sub(image_pattern, decode_image_url, markdown_str)
    return processed_markdown


def _dict_to_markdown_inner(data, indent=0):
    """
    Convert a dictionary to a Markdown formatted string.
    
    :param data: Dictionary to convert.
    :param indent: Initial indentation level.
    :return: String in Markdown format.
    """
    markdown_text = ''
    for key, value in data.items():
        # Adjust Markdown heading level based on indentation
        if indent == 0:
            markdown_text += f'\n## {str(key)}\n\n'
        elif indent == 1:
            markdown_text += f'\n### {str(key)}\n\n'
        elif indent == 2:
            markdown_text += f'\n#### {str(key)}\n\n'        
        elif indent == 3:
            markdown_text += f'\n##### {str(key)}\n\n'
        else:
            markdown_text += '\n' + '    ' * (indent - 1) + f'**{str(key)}**: \n\n'

        # Handle different types of values
        if isinstance(value, dict):
            if value:  # Only recurse if dictionary is not empty
                markdown_text += _dict_to_markdown_inner(value, indent + 1)
        elif isinstance(value, list):
            # Add a blank line before the list for better spacing
            markdown_text += '\n'
            if value:  # Only add list items if list is not empty
                for item in value:
                    if isinstance(item, dict):
                        # Recursively handle nested dictionaries within lists
                        markdown_text += '    ' * indent + '- ' + _dict_to_markdown_inner(item, indent + 1) + '\n\n'
                    else:
                        # Use code block for any item with length > 64 for better readability
                        #if len(str(item)) > 64:
                        #    markdown_text += '    ' * indent + f'- ```{str(item)}```\n\n'
                        #else:
                        #    # Standard list item with appropriate indentation
                        markdown_text += '    ' * indent + f'- {str(item)}\n\n'  # Extra newline for separation
        else:
            # Append short values inline, long values on the next line as a code block
            if len(str(value)) < 64:
                markdown_text = markdown_text.rstrip() + f' : {str(value)}\n\n'  # Ensure a blank line after
            else:
                markdown_text += f'```\n{str(value)}\n```\n\n'  # Code block for long text

    markdown_str = markdown_text.strip()
    return _process_markdown_images(markdown_str)

def _dict_info_to_markdown(extra_data):
    int_md = "" 
    try:
        if isinstance(extra_data, dict):
            int_md = _dict_to_markdown_inner(extra_data)
        elif extra_data is not None:
            int_md = str(extra_data) 
    except Exception as ex: # noqa
        logging.exception(str(ex))
    return int_md


# 根据用户输入生成最终回答、文件和图片的组合情况
def parse_final_result(result_dic):
    #user_input = result_dic.get("user_input", "")
    
    # 初始化返回内容
    content = ""
    files, images = [], []

    content = result_dic.get("response_answer", "")
    files = result_dic.get("lst_source_matches", [])
    images = result_dic.get("lst_image_names", [])

    return content, files, images

# 动态更新的进度内容生成器
def update_progress(progress_percentage, current_task, progress_log):
    html_content = f"""
    <div class="progress-container">
        <div class="progress-bar" style="width: {progress_percentage}%;"></div>
    </div>
    <div class="current-progress">当前进度: {current_task}</div>
    <div class="progress-log">进度日志:<br>{progress_log}</div>
    """
    return html_content

# on_clear：清空所有内容和控件状态
def on_clear():
    return (
        "进度: 等待用户操作",  # 进度信息重置为初始状态
        "",  # 清空 result_md 显示内容
        gr.update(value="没有文件可下载。", visible=False),  # 隐藏文件下载信息
        gr.update(value="图片名将在这里显示。", visible=False),  # 隐藏图片下载信息
        gr.update(value=None, visible=False),  # 清空并隐藏图片预览
        gr.update(value="", visible=False)  # 隐藏帮助内容
    )

# 帮助按钮的切换显示功能
g_count = 0
def toggle_help_content(is_help_visible):
    global g_count
    new_visibility = not is_help_visible  # 切换可见状态
    help_content = ""
    if new_visibility:
        help_content = f"{QUESTION_LIST}"
        if g_count % 2 == 0:
            status = ProgressLogger.get_progress_status()
            if len(status.keys()) != 0:
                extra_info = _dict_info_to_markdown(status)
                help_content += "\n\n" + extra_info
        g_count += 1
    
    help_content = help_content if new_visibility else ""
    return gr.update(value=help_content, visible=new_visibility), new_visibility

# 模拟提交功能，使用 parse_final_result 函数
def on_submit(user_input):
    ProgressLogger.clear_progress_history()
    prgs = ProgressLogger.get_progress_history()
    last_prgs_count = len(prgs)

    thread_main = threading.Thread(target=main_loop_gradio,
                                args=(user_input,))

    thread_main.start()
    progress_log = ""
    while True:
        time.sleep(1)

        prgs = ProgressLogger.get_progress_history()
        prgs_count = len(prgs)

        if prgs_count == last_prgs_count:
            continue

        last_prg = prgs[-1]

        progress_percentage = last_prg["percentage"]
        if last_prg['extra_info'] is not None:
            current_task = f"{last_prg['task_name']}#{last_prg['extra_info']}"
        else:
            current_task = f"{last_prg['task_name']}"

        for ndx in range(last_prgs_count, prgs_count):
            prg = prgs[ndx]
            if prg['extra_info'] is not None:
                progress_log += f"Step{prg['step']}: {prg['task_name']}#{prg['extra_info']}<br>"
            else:
                progress_log += f"Step{prg['step']}: {prg['task_name']}<br>"

        last_prgs_count = prgs_count
        yield (
            update_progress(progress_percentage, current_task, progress_log),  # 更新进度HTML
            "",  # 保持 result_md 内容为空，等待最终结果
            gr.update(visible=False),  # 隐藏 file_name_md
            gr.update(visible=False),  # 隐藏 image_name_md
            gr.update(value=None, visible=False),  # 清空并隐藏图片显示
        )

        if progress_percentage >= 99.9:
            break
    
    time.sleep(1)
    thread_main.join()

    result_dic = get_main_ret()

    # 使用 parse_final_result 获取回答内容、文件和图片组合情况
    result_dic["user_input"] = user_input
    content, files, images = parse_final_result(result_dic)

    # 生成文件和图片的下载链接
    #root_dir = "http://your-server-address"
    # 生成文件下载链接的HTML
    file_links_html = (
        "<p>相关的文件：</p><ul>" + "".join(
            [f"<li><a href='file://{html.escape(file)}' download>{os.path.basename(file)}</a></li>"
            for file in files]
        ) + "</ul>" if files else "<p>没有文件可下载。</p>"
    )

    # 生成图片下载链接的HTML
    image_links_html = (
        "<p>相关的图片：</p><ul>" + "".join(
            [f"<li><a href='file://{html.escape(img)}' download>{os.path.basename(img)}</a></li>"
            for img in images]
        ) + "</ul>" if images else "<p>没有图片可下载。</p>"
    )

    yield (
        update_progress(100, "所有任务完成", progress_log),
        content,  # 显示最终回答内容
        gr.update(value=file_links_html, visible=bool(files)),  # 文件名和下载链接HTML
        gr.update(value=image_links_html, visible=bool(images)),  # 图片名和下载链接HTML
        gr.update(value=images if images else None, visible=bool(images))  # 显示/隐藏图片列表
    )

# 构建界面的函数
def create_interface():
    with gr.Blocks(css=CUSTOM_CSS) as demo:  # 外部加载CSS
        # 应用标题
        app_title = gr.Markdown(f"# 多模态RAG Demo", elem_id="app_title") # noqa
        
        # 用户输入框
        user_inputbox = gr.Textbox(label="请输入您的问题", placeholder="在此输入问题，例如：典型问题看帮助", lines=2)
        
        # 按钮组
        with gr.Row():
            submit_btn = gr.Button("提交")
            clear_btn = gr.Button("清理")
            help_btn = gr.Button("帮助")
        
        # 进度HTML
        progress_html = gr.HTML("进度: 等待用户操作", elem_id="progress_html")
        
        # 结果的正文部分
        result_md = gr.Markdown(elem_id="result_md", value="结果将在这里显示。")
        
        # 文件下载部分：展示文件名和下载链接
        file_name_html = gr.HTML("没有文件可下载。", visible=False, elem_classes="file-and-image-section")  # 动态生成下载链接
        
        # 图片下载和显示部分：展示图片名和下载链接，图片预览
        image_name_html = gr.HTML("图片名将在这里显示。", visible=False, elem_classes="file-and-image-section")  # 动态生成下载链接
        image_display = gr.Gallery(label="图片显示区域", visible=False, elem_classes="file-and-image-section", preview=False)  # 图片预览

        
        # 帮助内容，初始为隐藏状态
        help_content_md = gr.Markdown("帮助内容将在这里显示。", visible=False, elem_id="help_content_md")
        
        # 版本说明
        version_info = gr.Markdown(f"版本: {get_git_version()} model:{get_gpt_model()}", elem_classes="version-info")  # noqa
        
        # 定义一个状态变量来保存帮助内容的可见性
        help_visible_state = gr.State(value=False)
        
        # 为按钮绑定点击事件
        submit_btn.click(
            fn=on_submit,
            inputs=user_inputbox,
            outputs=[
                progress_html, result_md, file_name_html, image_name_html, 
                image_display
            ]
        )
        
        clear_btn.click(
            fn=on_clear,
            outputs=[
                progress_html, result_md, file_name_html, image_name_html, 
                image_display, help_content_md
            ]
        )
        
        help_btn.click(
            fn=toggle_help_content,
            inputs=help_visible_state,
            outputs=[help_content_md, help_visible_state]
        )
    
    return demo

# 启动界面
if __name__ == "__main__":
    setup_logger_handlers()
    ProgressLogger._setup_handler()

    interface = create_interface()
    interface.launch(share=False)
