CUSTOM_CSS = """
/* 禁止下载任何字体，映射不熟悉的字体到系统字体 */
@font-face {
    font-family: '*';  /* 通配符匹配所有未知字体 */
    src: local('Arial') !important;  /* 默认映射到 Arial */
    font-display: swap !important;  /* 立即使用后备字体 */
}

/* 禁止所有字体下载 */
@import url("") !important;  /* 阻止所有 @import 的字体 */
@font-face { src: none !important; }  /* 禁止所有字体下载 */

/* 特定字体映射 */
@font-face {
    font-family: 'Source Sans Pro';
    src: local('Arial') !important;
}

@font-face {
    font-family: 'IBM Plex Mono';
    src: local('Courier New') !important;
}

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
    height: auto;
    overflow: hidden;
    display: block;
    padding: 10px;
    box-sizing: border-box;
}

/* 进度条容器 */
.progress-container {
    background-color: #f3f3f3;
    border-radius: 5px;
    height: 20px;
    width: 100%;
    overflow: hidden;
    margin-bottom: 8px;
}

.progress-bar {
    height: 100%;
    width: 0%;
    background-color: #4caf50;
    transition: width 0.4s ease;
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
    background-color: #FFFBEA;
    color: #333;
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 10px;
}

/* 文件和图片区域 - 淡青色背景 */
.file-and-image-section {
    background-color: #E0F7FA;
    color: #333;
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 10px;
}

/* 帮助内容区域 - 淡绿色背景 */
#help_content_md {
    background-color: #E8F5E9;
    color: #333;
    padding: 10px;
    border-radius: 5px;
}

/* 控件的统一间距和布局 */
.gr-button, .gr-textbox, .gr-markdown, .gr-gallery {
    margin-top: 10px;
    display: block;
}

/* 下载部分的布局 */
.download-section {
    display: flex;
    align-items: center;
    gap: 10px;
}

.download-section .button {
    flex: 0 0 10%;
}

.download-section .file-name {
    flex: 1;
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
        background-color: #4E4E2C;
        color: #FFFBEA;
    }

    .file-and-image-section {
        background-color: #37474F;
        color: #E0F7FA;
    }

    #help_content_md {
        background-color: #2E7D32;
        color: #E8F5E9;
    }
}

/* 确保 Gallery 中的图片按比例显示，不被裁剪 */
.file-and-image-section img {
    object-fit: contain;
    width: 100%;
    height: auto;
}
"""