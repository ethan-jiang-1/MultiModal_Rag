PROMPT_INSTRUCT_OCR_QWEN = """ 
#指令： 请OCR 整幅图，用maekdown 输出完整内容.  主要识别工整的印刷体，表格尽量恢复原貌， 手写体不用识别。
#输出格式： JSON
{
"markdown": "<OCR 恢复内容>",
"comment": "<恢复的说明等>“
}
"""  
