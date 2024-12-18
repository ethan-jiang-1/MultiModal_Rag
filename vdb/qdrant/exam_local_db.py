from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct
from typing import List, Dict, Optional
import numpy as np
import rich
import uuid

VECTOR_LEN = 128


def get_client(db_path: Optional[str] = None) -> QdrantClient:
    """
    获取 Qdrant 客户端。
    :param db_path: 数据库路径，如果为 None，则使用默认路径 "_vdb"。
    :return: Qdrant 客户端实例。
    """
    if db_path is None:
        db_path = "_vdb"
    client = QdrantClient(path=db_path)  # 数据会保存在此路径
    return client


def create_collection(client: QdrantClient, collection_name: str) -> None:
    """
    创建集合并插入随机向量数据。
    :param client: Qdrant 客户端实例。
    :param collection_name: 集合名称。
    """
    # 创建集合
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=VECTOR_LEN, distance=Distance.COSINE),
    )

    # 创建随机向量数据和对应的元数据
    vectors = np.random.rand(5, VECTOR_LEN).tolist()  # 生成 5 个随机向量，每个 128 维
    payloads = [{"info": f"vector_{i}", "meta": f"meta_{i}", "num":i} for i in range(len(vectors))]  # 元数据

    points = [
        PointStruct(id=str(uuid.uuid4()), vector=vectors[i], payload=payloads[i])  # 使用 UUID 作为 ID
        for i in range(len(vectors))
    ]

    # 插入向量到集合
    client.upsert(
        collection_name=collection_name,
        points=points,
    )

    print(f"Successfully inserted {len(vectors)} vectors into '{collection_name}'!")


def query_content(client: QdrantClient, collection_name: str, query_vector: List[float]) -> List[PointStruct]:
    """
    查询集合中与指定向量最相似的点。
    :param client: Qdrant 客户端实例。
    :param collection_name: 集合名称。
    :param query_vector: 查询向量。
    :return: 查询结果列表，每个结果为 PointStruct。
    """
    # 搜索最相似的 3 个向量
    results = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=3,  # 返回前 3 个最相似的结果
    )

    return results

def query_multiple_collections(
    client: QdrantClient, 
    collections: List[str], 
    query_vector: List[float], 
    limit_per_collection: int = 3
) -> List[Dict]:
    """
    在多个集合中查询内容并合并结果。

    :param client: Qdrant 客户端实例。
    :param collections: 要查询的集合列表。
    :param query_vector: 查询向量。
    :param limit_per_collection: 每个集合返回的结果限制数量。
    :return: 合并的查询结果列表，按相似度排序。
    """
    combined_results = []

    # 遍历所有集合并执行查询
    for collection in collections:
        if not client.collection_exists(collection):
            print(f"Collection '{collection}' does not exist, skipping...")
            continue

        # 查询当前集合
        results = client.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=limit_per_collection,  # 每个集合返回的结果数
        )

        # 将结果添加到合并列表中
        for result in results:
            combined_results.append({
                "collection": collection,
                "id": result.id,
                "score": result.score,
                "payload": result.payload,
            })

    # 根据相似度分数（score）降序排序
    combined_results.sort(key=lambda x: x["score"], reverse=True)

    return combined_results


def dump_database(client: QdrantClient, collection_name: str, with_vectors: bool = False) -> List[Dict]:
    """
    导出指定集合的所有点。
    :param client: Qdrant 客户端实例。
    :param collection_name: 集合名称。
    :return: 集合中所有点的列表，每个点是包含 id, vector 和 payload 的字典。
    """
    # 检查集合是否存在
    if not client.collection_exists(collection_name):
        print(f"Collection '{collection_name}' does not exist.")
        return []

    # 滚动获取集合中的所有点
    all_results = []
    has_more = True
    next_page_offset = None

    while has_more:
        # 调用 scroll 方法
        result = client.scroll(
            collection_name=collection_name,
            offset=next_page_offset,
            limit=100,  # 每次滚动返回的点数
            with_vectors=with_vectors,  # 包含向量数据
            with_payload=True
        )
        # 添加点到结果列表
        all_results.extend(result[0])

        # 更新滚动参数
        next_page_offset = result[1]
        has_more = next_page_offset is not None

    return all_results


if __name__ == "__main__":
    collection_names = ["collect1", "collect2"]
    query_vector = np.random.rand(VECTOR_LEN).tolist()  # 随机生成一个查询向量
    client = get_client()
        
    for collection_name in collection_names:
        create_collection(client, collection_name)

        results = query_content(client, collection_name, query_vector)
        for ndx, result in enumerate(results):
            rich.print(f"[blue]Result {ndx + 1}[/blue]:", result)

        #client.close()

    #clien = get_client()
    results = query_multiple_collections(client, collection_names, query_vector)
    for ndx, result in enumerate(results):
        rich.print(f"[pink]Result {ndx + 1}[/pink]:", result)
    #client.close()

    #client = get_client()
    all_results = dump_database(client, collection_name)
    rich.print(all_results)
    
    
    client.close()
