from typing import List
import requests
import json
import os
import rich
from dotenv import load_dotenv

load_dotenv()


def jina_rerank(query_str:str, documents: List[str], top_n: int = None):

    url = 'https://api.jina.ai/v1/rerank'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {os.getenv("JINA_API_KEY")}'
    }
    data = {
        "model": "jina-reranker-v2-base-multilingual",
        "query":  query_str,
        "top_n": top_n,
        "documents": documents
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    results = response.json()["results"]
    return results

if __name__ == "__main__":
    query_str = "Organic skincare products for sensitive skin"
    documents = [
            "Organic skincare for sensitive skin with aloe vera and chamomile: Imagine the soothing embrace of nature with our organic skincare range, crafted specifically for sensitive skin. Infused with the calming properties of aloe vera and chamomile, each product provides gentle nourishment and protection. Say goodbye to irritation and hello to a glowing, healthy complexion.",
            "New makeup trends focus on bold colors and innovative techniques: Step into the world of cutting-edge beauty with this seasons makeup trends. Bold, vibrant colors and groundbreaking techniques are redefining the art of makeup. From neon eyeliners to holographic highlighters, unleash your creativity and make a statement with every look.",
            "Bio-Hautpflege für empfindliche Haut mit Aloe Vera und Kamille: Erleben Sie die wohltuende Wirkung unserer Bio-Hautpflege, speziell für empfindliche Haut entwickelt. Mit den beruhigenden Eigenschaften von Aloe Vera und Kamille pflegen und schützen unsere Produkte Ihre Haut auf natürliche Weise. Verabschieden Sie sich von Hautirritationen und genießen Sie einen strahlenden Teint.",
            "Neue Make-up-Trends setzen auf kräftige Farben und innovative Techniken: Tauchen Sie ein in die Welt der modernen Schönheit mit den neuesten Make-up-Trends. Kräftige, lebendige Farben und innovative Techniken setzen neue Maßstäbe. Von auffälligen Eyelinern bis hin zu holografischen Highlightern – lassen Sie Ihrer Kreativität freien Lauf und setzen Sie jedes Mal ein Statement.",
            "Cuidado de la piel orgánico para piel sensible con aloe vera y manzanilla: Descubre el poder de la naturaleza con nuestra línea de cuidado de la piel orgánico, diseñada especialmente para pieles sensibles. Enriquecidos con aloe vera y manzanilla, estos productos ofrecen una hidratación y protección suave. Despídete de las irritaciones y saluda a una piel radiante y saludable.",
            "Las nuevas tendencias de maquillaje se centran en colores vivos y técnicas innovadoras: Entra en el fascinante mundo del maquillaje con las tendencias más actuales. Colores vivos y técnicas innovadoras están revolucionando el arte del maquillaje. Desde delineadores neón hasta iluminadores holográficos, desata tu creatividad y destaca en cada look.",
            "针对敏感肌专门设计的天然有机护肤产品：体验由芦荟和洋甘菊提取物带来的自然呵护。我们的护肤产品特别为敏感肌设计，温和滋润，保护您的肌肤不受刺激。让您的肌肤告别不适，迎来健康光彩。",
            "新の化粧トレンドは大胆な色と革新的なテクニックに焦点を当てています: 最新の化粧トレンドで美しさの現代を体験してください。大胆で鮮やかな色と革新的な技術は、メイクのアートを再定義しています。ネオンアイライナーやホログラフィックハイライターなど、あらゆる見た目にクリエイティビティを解放し、ステートメントを打ち出してください。"
        ]
    results = jina_rerank(query_str, documents)
    rich.print(results)
