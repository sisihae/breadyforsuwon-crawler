-- PostgreSQL bakery 테이블 생성 쿼리
CREATE TABLE IF NOT EXISTS bakery (
    id VARCHAR(32) PRIMARY KEY,  
    name VARCHAR(255) NOT NULL,
    rating FLOAT,
    address VARCHAR(512)
);

-- Qdrant 컬렉션 생성 예시 (Python, 참고용)
--
-- from qdrant_client import QdrantClient
-- client = QdrantClient(host="localhost", port=6333)
-- client.recreate_collection(
--     collection_name="bakery_summaries",
--     vectors_config={"size": 768, "distance": "Cosine"},
-- ) 