# 定义 CSS 样式
CUSTOM_CSS = """
/* 重置所有字体相关设置 */
* {
    font: initial !important;
    font-family: system-ui, -apple-system, sans-serif !important;
    font-display: block !important;
    font-feature-settings: normal !important;
    font-kerning: none !important;
    font-optical-sizing: none !important;
    font-variation-settings: normal !important;
    font-palette: normal !important;
    font-synthesis: none !important;
    text-rendering: optimizeSpeed !important;
}

/* 阻止所有外部资源加载 */
@import none !important;
@import url("data:,") !important;

/* 禁用所有字体加载 */
@font-face {
    font-family: '*';
    src: none !important;
    font-display: block !important;
}

/* 覆盖特定字体 */
@font-face {
    font-family: 'Source Sans Pro';
    src: local('system-ui') !important;
}

@font-face {
    font-family: 'IBM Plex Mono';
    src: local('Courier New') !important;
}

/* 禁用所有远程资源加载 */
[style*="@import"],
[style*="url("],
[style*="fonts.googleapis"],
[style*="fonts.gstatic"],
[style*="//"],
[style*="http"],
[style*="https"] {
    display: none !important;
}

/* 强制使用系统字体 */
.gradio-container,
.gradio-container *,
#component-0,
#component-0 * {
    font-family: system-ui, -apple-system, sans-serif !important;
}

/* 禁用所有动画和过渡 */
* {
    animation: none !important;
    transition: none !important;
}

/* 阻止网络请求 */
link[rel="stylesheet"][href*="fonts.googleapis.com"],
link[rel="stylesheet"][href*="fonts.gstatic.com"] {
    display: none !important;
}

/* 禁用字体平滑和优化 */
html {
    -webkit-font-smoothing: none !important;
    -moz-osx-font-smoothing: none !important;
    text-rendering: optimizeSpeed !important;
}

/* 强制立即渲染 */
body {
    font-display: block !important;
}

/* 设置资源加载超时 */
@import url("data:,") !important;  /* 使用空的 data URL */

/* 设置字体加载超时 */
* {
    font-display: optional !important;  /* 如果3秒内没加载完就使用系统字体 */
}

/* 添加资源加载超时 */
@media all {
    @font-face {
        font-family: '*';
        src: local('system-ui') !important;
        font-display: swap !important;
        unicode-range: U+0-10FFFF;
        font-weight: 100 900;
        font-style: normal;
        font-stretch: normal;
        font-variant: normal;
        font-feature-settings: normal;
        font-variation-settings: normal;
        size-adjust: none;
        advance-override: none;
        baseline-override: none;
        descent-override: none;
        ascent-override: none;
        line-gap-override: none;
    }
}
"""