import json
import re
from openai import AzureOpenAI
from dotenv import load_dotenv
import sys
import os
from pix2text import Pix2Text
sys.path.append("./")

from llm_prompt import get_content_prompt,md_correct_prompt,md_self_correct_prompt
from unstructured.partition.pdf import partition_pdf
load_dotenv()

def get_pdfs_in_directory(directory):
    pdf_files = [f for f in os.listdir(directory) if f.endswith('.pdf')]
    return pdf_files

def pdf2md(base_path,pdf_path,md_name):
    p2t = Pix2Text.from_config(enable_formula=False)
    doc = p2t.recognize_pdf(pdf_path)
    od=base_path+'/mds/s0_md_unstructured/'
    doc.to_markdown(out_dir=od,markdown_fn=md_name)


def get_uns_content(file_path):
    elements = partition_pdf(file_path)
    str_list=[str(el).replace("保密信息","").replace("技术服务合同 V5.0","") for el in elements]
    new_list = [re.sub(r'第\d+页/共\d+页', '', str) for str in str_list]
    return "\n".join(new_list)

def get_md_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        md_text = file.read()
    file.close()
    return md_text

def get_all_content(text_file,md_file):
    client=AzureOpenAI(api_key=os.getenv("OPENAI_API_KEY"),azure_endpoint=os.getenv("OPENAI_BASE_URL"),api_version="2024-02-15-preview")
    md_text=get_md_content(md_file)
    content=get_uns_content(text_file)
    try:
        prompt=get_content_prompt.format(Content=content)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1
            )
        text = response.choices[0].message.content
        res=json.loads(text.replace("```","").replace("json",""))
        text=res['content']
        prompt=md_correct_prompt.format(text1=text,markdown=md_text)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1
            )
        text = response.choices[0].message.content
        res=json.loads(text.replace("```","").replace("json",""))
        return res['content']
    except:
        prompt=md_self_correct_prompt.format(markdown=md_text)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1
            )
        text = response.choices[0].message.content
        res=json.loads(text.replace("```","").replace("json",""))
        text=res['content']
        return text



directory_path = 'raw'
#获取所有.pdf文件
pdfs=get_pdfs_in_directory(directory_path)
#初步处理pdf2md
#base_path = os.getcwd()
#for fname in pdfs:
    #pdf2md(base_path,base_path+'/'+directory_path+'/'+fname,fname+'.step0.md')
    #print(fname+'.step0.md已生成')
#得到最终pdf2md文件，在mds/s1_md_final/下
for fname in pdfs:
    print(fname)
    #获取更新后的md
    content=get_all_content('raw/'+fname,'mds/s0_md_unstructured/'+fname+'.step0.md')
    with open('mds/s1_md_final/'+fname+'.step1.md','w',encoding='utf-8') as file:
        file.write(content)
