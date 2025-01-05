import time
from typing import List, Tuple, Any, Generator
import gradio as gr
import threading
import os
import html
import logging 
import re
import rich
import urllib.parse
from gradio.themes.utils import fonts
from gradio.themes import Base
from dotenv import load_dotenv

load_dotenv()

from mrag_app._app_gradio_css import CUSTOM_CSS
from mrag_app._app_questions import QUESTION_LIST_MRAG, QUESTION_LIST_PAPERS
from mrag_app._app_qa_core import main_loop_gradio, get_rag_response_from_main_loop, reset_rag_response_for_main_loop, RagResponse
from mrag_app._app_log_monitor import ProgressLogger
from mrag_vdb.utils.util_logging import setup_logger_handlers
from mrag_vdb.utils.util_git import get_git_version
from mrag_vdb.dto.runtime_settings import ModelGptSel, KbNameSel, RetrievalNum

# 设置更多环境变量来控制字体加载
os.environ["GRADIO_USE_LOCAL_FONTS"] = "True"
# 新增：禁用预加载
os.environ["GRADIO_DISABLE_PRELOAD"] = "True"
# 新增：强制使用本地资源
os.environ["GRADIO_OFFLINE_MODE"] = "True"

# 完全禁用 Gradio 的字体系统
fonts.GoogleFont.url_template = ""
fonts.GoogleFont.cache = {}

# 设置 Gradio 的全局超时
gr.context.timeout = 3  # 3秒超时

# 修改 Gradio 的字体加载行为
def _monkey_patch_gradio():
    # 尝试修改 Gradio 内部的字体加载机制
    if hasattr(gr, 'themes') and hasattr(gr.themes, 'utils'):
        gr.themes.utils.get_theme_assets = lambda: []
        gr.themes.utils.get_fonts = lambda: []

_monkey_patch_gradio()

def _process_markdown_images(markdown_str: str) -> str:
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


def _dict_to_markdown_inner(data: dict, indent: int = 0) -> str:
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

def _dict_info_to_markdown(extra_data: dict) -> str:
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
def parse_content_from_rag_response(rag_response: RagResponse) -> Tuple[str, str, List[Tuple[str, str, str]], List[Tuple[str, str, str]]]:
    """
    Parse content from RagResponse into display-ready format
    
    Returns:
        Tuple containing:
        - content: Main answer text
        - content_details: Detailed answer with references
        - source_tuples: List of (name, title, path) for source documents
        - image_tuples: List of (name, title, path) for images
    """
    # 从 rag_answer 中获取主要内容
    content = rag_response.rag_answer.answer
    content_details = rag_response.rag_answer.answer_referenced

    # 源文档信息
    srcs_name_title_pname = list(zip(
        rag_response.rag_answer.source_names,
        rag_response.rag_answer.source_titles,
        rag_response.rag_answer.source_pnames
    ))

    # 图片信息
    imgs_name_title_pname = list(zip(
        rag_response.rag_answer.image_names,
        rag_response.rag_answer.image_titles,
        rag_response.rag_answer.image_pnames
    ))

    return content, content_details, srcs_name_title_pname, imgs_name_title_pname

# 动态更新的进度内容生成器
def update_progress(progress_percentage: int, current_task: str, progress_log: str) -> str:
    html_content = f"""
    <div class="progress-container">
        <div class="progress-bar" style="width: {progress_percentage}%;"></div>
    </div>
    <div class="current-progress">当前进度: {current_task}</div>
    <div class="progress-log">进度日志:<br>{progress_log}</div>
    """
    return html_content

# on_clear：清空所有内容和控件状态
def on_clear() -> Tuple[str, str, str, str, str]:
    reset_rag_response_for_main_loop()
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
def toggle_help_content(is_help_visible: bool) -> Tuple[str, bool]:
    global g_count
    new_visibility = not is_help_visible  # 切换可见状态
    help_content = ""
    if new_visibility:
        if KbNameSel.get_kbname() == "mrag":
            help_content = QUESTION_LIST_MRAG
        elif KbNameSel.get_kbname() == "papers":
            help_content = QUESTION_LIST_PAPERS
        if g_count % 2 == 0:
            status = ProgressLogger.get_progress_status()
            if len(status.keys()) != 0:
                extra_info = _dict_info_to_markdown(status)
                help_content += "\n\n" + extra_info
        g_count += 1
    
    help_content = help_content if new_visibility else ""
    return gr.update(value=help_content, visible=new_visibility), new_visibility

# 模拟提交功能，使用 parse_final_result 函数
def on_submit(user_input: str) -> Generator[Tuple[Any, Any, Any, Any, Any], None, None]:
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

    rag_response = get_rag_response_from_main_loop()

    # 使用 parse_final_result 获取回答内容、文件和图片组合情况
    rag_response.user_input = user_input
    content, content_details, srcs_name_title_pname, imgs_name_title_pname = parse_content_from_rag_response(rag_response)
    rich.print(content)
    rich.print(content_details)
    rich.print(srcs_name_title_pname)
    rich.print(imgs_name_title_pname)

    # 生成文件和图片的下载链接
    #root_dir = "http://your-server-address"
    # 生成文件下载链接的HTML
    file_links_html = (
        "<p>相关的文件：</p><ul>" + "".join(
            [f"<li><a href='file://{html.escape(name_title_pname[2])}' download>{os.path.basename(name_title_pname[0])}</a></li>"
            for name_title_pname in srcs_name_title_pname]
        ) + "</ul>" if srcs_name_title_pname else "<p>没有文件可下载。</p>"
    )

    # 生成图片下载链接的HTML
    image_links_html = (
        "<p>相关的图片：</p><ul>" + "".join(
            [f"<li><a href='file://{html.escape(name_title_pname[2])}' download>{os.path.basename(name_title_pname[0])}</a></li>"
            for name_title_pname in imgs_name_title_pname]
        ) + "</ul>" if imgs_name_title_pname else "<p>没有图片可下载。</p>"
    )

    yield (
        update_progress(100, "所有任务完成", progress_log),
        content,  # 显示最终回答内容
        gr.update(value=file_links_html, visible=bool(srcs_name_title_pname)),  # 文件名和下载链接HTML
        gr.update(value=image_links_html, visible=bool(imgs_name_title_pname)),  # 图片名和下载链接HTML
        gr.update(value=[ntp[2] for ntp in imgs_name_title_pname] if imgs_name_title_pname else None, visible=bool(imgs_name_title_pname))  # 显示/隐藏图片列表
    )

def _get_version_info() -> str:
    return f"mrag: {get_git_version()} gradio:{gr.__version__} model:{ModelGptSel.get_gpt_model()} kbname: {KbNameSel.get_kbname()} rtv_num: {RetrievalNum.get_retrieval_num()}"

# 更新版本信息和状态的函数
def on_update_model(selected_model: str) -> str:
    # 更新显示的版本信息和状态
    ModelGptSel.set_gpt_model(selected_model)
    return _get_version_info()

def on_update_kbname(selected_kbname: str) -> str:
    KbNameSel.set_kbname(selected_kbname)
    return _get_version_info()

def on_update_rtvnum(selected_num: str) -> str:
    RetrievalNum.set_retrieval_num(int(selected_num))
    return _get_version_info()
# 创建自定义主题
class LocalFontTheme(Base):
    def __init__(self):
        super().__init__()
        # 不能设为 None，但可以使用一个空的 GoogleFont 对象
        self.font = fonts.GoogleFont("Arial")
        self.font_mono = fonts.GoogleFont("Courier New")
        # 直接使用系统字体
        self.font_family = "system-ui, -apple-system, sans-serif"
        self.font_mono_family = "Courier New, monospace"


# 构建界面的函数
def create_interface() -> gr.Blocks:
    # 使用自定义主题和 CSS
    custom_theme = LocalFontTheme()
    
    with gr.Blocks(
        css=CUSTOM_CSS, 
        theme=custom_theme,
    ) as demo:
        # 应用标题
        app_title = gr.Markdown(f"# 多模态RAG ", elem_id="app_title") # noqa
        
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
        
        with gr.Row():
            # 模型选择部分
            model_selector = gr.Radio(
                choices=ModelGptSel.SUPPORTED_MODELS, 
                value=ModelGptSel.get_gpt_model(), 
                label="选择模型", 
                elem_id="model_selector"
            )

            # KBNAME
            kbname_selector = gr.Radio(
                choices=KbNameSel.SUPPORTED_KBNAMES,
                value=KbNameSel.get_kbname(), 
                label="选择知识库", 
                elem_id="kbname_selector"
            )

            # RetrivalNum
            rtvnum_selector = gr.Radio(
                choices=RetrievalNum.SUPPORTED_NUMS,
                value=RetrievalNum.get_retrieval_num(), 
                label="选择搜索条数", 
                elem_id="rtvnum_selector"
            )

        # 版本说明
        version_info = gr.Markdown(_get_version_info(), elem_classes="version-info")  # noqa
        
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

        # 模型选择事件绑定
        model_selector.change(
            fn=on_update_model,
            inputs=[model_selector],
            outputs=[version_info]
        )

        kbname_selector.change(
            fn=on_update_kbname,
            inputs=[kbname_selector],
            outputs=[version_info]
        )

        rtvnum_selector.change(
            fn=on_update_rtvnum,
            inputs=[rtvnum_selector],
            outputs=[version_info]
        )      

    return demo

# 启动界面
if __name__ == "__main__":
    setup_logger_handlers()
    ProgressLogger._setup_handler()

    interface = create_interface()
    interface.launch(share=False)
