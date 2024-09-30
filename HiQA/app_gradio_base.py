import time
import sys
import gradio as gr
import threading
import os
import html

if "./" not in sys.path:
    sys.path.append("./")

os.environ["GRADIO_USE_LOCAL_FONTS"] = "True"

from HiQA._app_base import CUSTOM_CSS, QUESTION_LIST
from HiQA._app_qa_core import main_loop_gradio, get_main_ret
from HiQA._app_log_monitor import ProgressLogger
from HiQA.utils.util_logging import setup_logger_handlers
from HiQA.qa_core import get_gpt_model
from HiQA.utils.util_git import get_git_version

# 根据用户输入生成最终回答、文件和图片的组合情况
def parse_final_result(result_dic):
    #user_input = result_dic.get("user_input", "")
    
    # 初始化返回内容
    content = ""
    files, images = [], []

    llm_response_json = result_dic.get("llm_response_json", None)
    if llm_response_json is not None:
        content = llm_response_json.get("answer")

    files = result_dic.get("lst_source_matches", [])
    image_n_title = result_dic.get("lst_image_n_title", None)
    if image_n_title is not None:
        images = [item["image"] for item in image_n_title]

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
def toggle_help_content(is_help_visible):
    new_visibility = not is_help_visible  # 切换可见状态
    help_content = f"{QUESTION_LIST}" if new_visibility else ""
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
        current_task = f"{last_prg['task_name']}#{last_prg['extra_info']}"

        for ndx in range(last_prgs_count, prgs_count):
            prg = prgs[ndx]
            progress_log += f"Step{prg['step']}: {prg['task_name']}#{prg['extra_info']}<br>"

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
    interface.launch()
