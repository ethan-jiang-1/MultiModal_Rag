from qdrant_client import QdrantClient

class QdrantClientContextManager:
    def __init__(self, *args, **kwargs):
        self.client = QdrantClient(*args, **kwargs)

    def __enter__(self):
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()