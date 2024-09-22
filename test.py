import requests

# 定义请求的URL
url = "http://region-42.seetacloud.com:29664/rerank/"
# ssh -p 26489 root@region-42.seetacloud.com
# 定义请求的数据
data = {
    "query": "Organic skincare products for sensitive skin",
    "documents": [
    "Organic skincare for sensitive skin with aloe vera and chamomile.",
    "New makeup trends focus on bold colors and innovative techniques",
    "Bio-Hautpflege für empfindliche Haut mit Aloe Vera und Kamille",
    "Neue Make-up-Trends setzen auf kräftige Farben und innovative Techniken",
    "Cuidado de la piel orgánico para piel sensible con aloe vera y manzanilla",
    "Las nuevas tendencias de maquillaje se centran en colores vivos y técnicas innovadoras",
    "针对敏感肌专门设计的天然有机护肤产品",
    "新的化妆趋势注重鲜艳的颜色和创新的技巧",
    "敏感肌のために特別に設計された天然有機スキンケア製品",
    "新しいメイクのトレンドは鮮やかな色と革新的な技術に焦点を当てています"
    ],
    "count": 5
}

# 发送POST请求
response = requests.post(url, json=data)

# 检查请求是否成功
if response.status_code == 200:
    # 打印返回的得分
    print(response.json())
else:
    print(f"Request failed with status code {response.status_code}: {response.text}")