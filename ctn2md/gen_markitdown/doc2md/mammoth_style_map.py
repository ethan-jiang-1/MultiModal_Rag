def get_mammoth_style_map():
    style_map = """
    p[style-name='heading 1'] => h1:fresh
    p[style-name='heading 2'] => h2:fresh
    p[style-name='heading 3'] => h3:fresh
    p[style-name='heading 4'] => h4:fresh
    p[style-name='heading 5'] => h5:fresh
    p[style-name='heading 6'] => h6:fresh
    p[style-name='标题 1'] => h1:fresh
    p[style-name='标题 2'] => h2:fresh
    p[style-name='标题 3'] => h3:fresh
    p[style-name='标题 4'] => h4:fresh
    p[style-name='标题 5'] => h5:fresh
    p[style-name='标题 6'] => h6:fresh
    p[style-name='Title'] => h1:fresh
    p[style-name='Subtitle'] => h2:fresh
    p[style-name='Normal'] => p:fresh
    p[style-name='dingdocnormal'] => p:fresh
    """
    return style_map