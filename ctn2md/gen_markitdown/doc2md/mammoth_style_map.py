_STYLE_MAP = """
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

def get_mammoth_style_map():
    return _STYLE_MAP

_KNOWN_HEADING_MAP = {
    'title': 'heading1',
    'subtitle': 'heading2',

    '标题 1': 'heading1', 
    '标题 2': 'heading2',
    '标题 3': 'heading3',
    '标题 4': 'heading4',
    '标题 5': 'heading5',
    '标题 6': 'heading6',

    'heading 1': 'heading1',
    'heading 2': 'heading2', 
    'heading 3': 'heading3',
    'heading 4': 'heading4',
    'heading 5': 'heading5',
    'heading 6': 'heading6',
    
    '标题1': 'heading1',
    '标题2': 'heading2',
    '标题3': 'heading3',
    '标题4': 'heading4',
    '标题5': 'heading5',
    '标题6': 'heading6',
    
    'Heading 1': 'heading1',
    'Heading 2': 'heading2',
    'Heading 3': 'heading3',
    'Heading 4': 'heading4',
    'Heading 5': 'heading5',
    'Heading 6': 'heading6',
    
    'h1': 'heading1',
    'h2': 'heading2',
    'h3': 'heading3',
    'h4': 'heading4',
    'h5': 'heading5',
    'h6': 'heading6',
    
    'header 1': 'heading1',
    'header 2': 'heading2',
    'header 3': 'heading3',
    'header 4': 'heading4',
    'header 5': 'heading5',
    'header 6': 'heading6',
    
    'chapter': 'heading1',
    'section': 'heading2',
    'subsection': 'heading3',
    '主标题': 'heading1',
    '副标题': 'heading2',
    '章节标题': 'heading1',
    '节标题': 'heading2',
    '小节标题': 'heading3'
}

def get_known_heading_map():
    return _KNOWN_HEADING_MAP
