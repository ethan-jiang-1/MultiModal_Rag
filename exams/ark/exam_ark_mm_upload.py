import rich 
import os
from openai import OpenAI


client = OpenAI(
    api_key=os.environ.get("ARK_API_KEY"),
    base_url="https://ark.cn-beijing.volces.com/api/v3",
)

# 需要传给大模型的图片
#from ctn2md.utils_llm.llm_base import upload_image_to_oss
#image_path = "_work/md_pdf_pages/5ec48698-page_1_rects.jpg"
#image_url = upload_image_to_oss(image_path)
#print(image_url)

image_url = "https://pdfpage.oss-cn-beijing.aliyuncs.com/20241224_5ec48698-page_1_rects.jpg?OSSAccessKeyId=LTAI5tAdksii7xo1vKZd8Uug&Expires=1735024865&Signature=FTv%2BKau86CftKtIDk4lzXYWodlI%3D"

user_prompt = """
Convert the following page into Markdown format, ensuring completeness and maintaining the original layout order.
- Recognize and convert text, lists, tables, and images:
- **Lists**: Use Markdown list format (`-` for unordered, numbers for ordered).
- **Tables**: Use Markdown table format.
- **Images**: Embed using `![Figure X](<Y: LocalImageFileName> "<Z: caption of the image content>")`.
- Use headings, paragraphs, lists, and tables for structure.
- Ensure image output is/are located at the right place in the markdown flow, do not simply put at end of the markdown. **do not miss** any image output with their caption.
- Ignore headers and footers.
- **Important**: Ensure the output text's language matches the original content exactly. **Do not translate** any text, and maintain the original language.
"""

# Image input:
response = client.chat.completions.create(
    model="ep-20241220100411-qb77p",
    messages=[
        {
            "role": "user",
            "content": [
                {   
                    "type": "text", 
                    "text": f"{user_prompt}"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"{image_url}"
                    }
                },
            ],
        }
    ],
)

choices0 = response.choices[0]
rich.print(choices0)

content = choices0.message.content
rich.print(content)