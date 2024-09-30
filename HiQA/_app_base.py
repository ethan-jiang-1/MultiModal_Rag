QUESTION_LIST = """
### 问题列表：
1. 前后座椅H点参考距离是多少？  
2. 椅背板与旁侧板的保留运动间隙是多少？  
3. 靠背最后位置时与侧板翻边的运动间隙是多少？  
4. 法规要求的前后排座椅距离是多少  
5. 前后排座椅距离的设计目标是多少？  
6. UN-R17圆角的法规要求是多少？/圆角法规  
7. UN-R17圆角的设计目标值是多少？/圆角目标值  
8. 乘员保护的圆角要求是多少？/圆角设计要求  
9. 座垫STO间隙要求是什么？  
10. 靠背STO间隙要求是什么？  
11. Ai在人力资源领域前景趋势  
12. 管理者的组织执行能力是什么？  
13. 该如何做好一个管理者  
14. 如何进行高效沟通  
15. 有哪些比亚迪的项目  
16. 有哪些关于电子电器的项目  
17. 考勤规则/考勤规则是什么  
18. 主管的培训课程涉及什么  
"""

# 定义 CSS 样式
CUSTOM_CSS = """
 /* 全局样式 */
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
}

/* 标题样式 */
#app_title {
    font-size: 24px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 20px;
}

/* 进度提示 */
#progress_html {
    font-size: 14px;
    line-height: 1.5;
    margin-bottom: 10px;
    height: auto; /* 根据内容自动调整高度 */
    overflow: hidden; /* 不显示滚动条，允许自动扩展 */
    display: block; /* 保证它是块级元素，支持页面流式布局 */
    padding: 10px; /* 适当内边距，保持内容清晰 */
    box-sizing: border-box; /* 包含内边距在高度计算内 */
    /* 保持默认背景，适用于正常模式和夜间模式 */
}

/* 进度条容器 */
.progress-container {
    background-color: #f3f3f3;
    border-radius: 5px;
    height: 20px; /* 固定进度条高度 */
    width: 100%;
    overflow: hidden;
    margin-bottom: 8px;
}

.progress-bar {
    height: 100%;
    width: 0%; /* 初始宽度为0%，根据进度调整 */
    background-color: #4caf50; /* 绿色进度条 */
    transition: width 0.4s ease; /* 平滑过渡效果 */
}

.current-progress {
    font-weight: bold;
    color: #333;
    margin-bottom: 5px;
}

.progress-log {
    font-size: 13px;
    color: #666;
    line-height: 1.4;
    margin-top: 5px;
}

/* 结果正文区域 - 淡黄色背景 */
#result_md {
    background-color: #FFFBEA; /* 正常模式淡黄色 */
    color: #333;
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 10px;
}

/* 文件和图片区域 - 淡青色背景 */
.file-and-image-section {
    background-color: #E0F7FA; /* 正常模式淡青色 */
    color: #333;
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 10px;
}

/* 帮助内容区域 - 淡绿色背景 */
#help_content_md {
    background-color: #E8F5E9; /* 正常模式淡绿色 */
    color: #333;
    padding: 10px;
    border-radius: 5px;
}

/* 控件的统一间距和布局 */
.gr-button, .gr-textbox, .gr-markdown, .gr-gallery {
    margin-top: 10px;
    display: block; /* 保持流式布局 */
}

/* 下载部分的布局 */
.download-section {
    display: flex;
    align-items: center;
    gap: 10px;
}

.download-section .button {
    flex: 0 0 10%; /* 按钮占据10%宽度 */
}

.download-section .file-name {
    flex: 1; /* 文件名占据剩余宽度 */
}

/* 版本信息的对齐和样式 */
.version-info {
    text-align: right;
    font-size: 12px;
    color: #888;
    margin-top: 20px;
}

/* 夜间模式 */
@media (prefers-color-scheme: dark) {
    #progress_html {
        color: #fff;
    }

    #result_md {
        background-color: #4E4E2C; /* 夜间模式的淡黄 */
        color: #FFFBEA; /* 适合淡黄背景 */
    }

    .file-and-image-section {
        background-color: #37474F; /* 夜间模式的淡青 */
        color: #E0F7FA; /* 适合淡青背景 */
    }

    #help_content_md {
        background-color: #2E7D32; /* 夜间模式的淡绿 */
        color: #E8F5E9; /* 适合淡绿背景 */
    }
}

/* 确保 Gallery 中的图片按比例显示，不被裁剪 */
.file-and-image-section img {
    object-fit: contain; /* 按比例缩放，保证完整显示 */
    width: 100%; /* 图片宽度适应容器 */
    height: auto; /* 高度自动调整，保持图片比例 */
}
"""