import dashscope


dashscope.api_key = "sk-a7cb64d9e5124609ac52849950c6fee2"
def generate_image_description(image_url):
    messages = [{
        'role': 'user',
        'content': [
            {
                'image': image_url
            },
            {
                'text': '请简单描述一下这张图片。'
            },
        ]
    }]
    # The model name 'qwen-vl-max-0809' is the identity of 'Qwen2-VL-72B'.
    response = dashscope.MultiModalConversation.call(model='qwen-vl-max-0809', messages=messages)
    return response["output"]["choices"][0]["message"]["content"][0]["text"]

if __name__ == '__main__':
    image_url = 'E:/MultiModal_Rag/HiQA/datasets/test/images/AIGC时代的人力资源管理进化(徐刚)/AIGC时代的人力资源管理进化(徐刚)_imgbmp_9_8.png'
    print(generate_image_description(image_url))