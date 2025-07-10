from django.db import models

class Bakery(models.Model):
    id = models.BigIntegerField(primary_key=True)  # CSV의 id
    name = models.CharField(max_length=255)
    rating = models.FloatField(null=True, blank=True)
    address = models.CharField(max_length=512)

    def __str__(self):
        return f"{self.name} ({self.id})"

# 실제 Qdrant는 스키마리스지만, 컬렉션 생성 시 벡터 크기와 필드 정의 필요

QDRANT_COLLECTION_NAME = "bakery_summaries"
QDRANT_VECTOR_SIZE = 768  # 임베딩 차원

QDRANT_PAYLOAD_SCHEMA = {
    "bakery_id": "int",  # RDB의 PK와 동일
    "summary": "str",    
    # "vector": [float]   # 임베딩 벡터 (Qdrant에 자동 저장)
}

# Qdrant collection 생성 in Python
# from qdrant_client import QdrantClient
# client = QdrantClient(host="localhost", port=6333)
# client.recreate_collection(
#     collection_name=QDRANT_COLLECTION_NAME,
#     vectors_config={"size": QDRANT_VECTOR_SIZE, "distance": "Cosine"},
# ) 