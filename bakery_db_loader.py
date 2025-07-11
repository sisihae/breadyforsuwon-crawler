import pandas as pd
import psycopg2
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer  

df = pd.read_csv('bakery_list.csv')

pg_conn = psycopg2.connect(
    dbname='your_db', user='your_user', password='your_pw', host='your_host', port=5432
)
pg_cur = pg_conn.cursor()

qdrant = QdrantClient(host="localhost", port=6333)
COLLECTION_NAME = "bakery_summaries"
VECTOR_SIZE = 768  # 임베딩 차원

# 4. 임베딩 모델 준비 (예: KoBERT, all-MiniLM 등)
model = SentenceTransformer('jhgan/ko-sroberta-multitask')  

for _, row in df.iterrows():
    bakery_id = str(row['id']) 
    name = row['name']
    rating = float(row['rating']) if not pd.isnull(row['rating']) else None
    address = row['address']
    aisummary = row['aisummary']

    pg_cur.execute(
        "INSERT INTO bakery (id, name, rating, address) VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
        (bakery_id, name, rating, address)
    )

    embedding = model.encode(aisummary).tolist()
    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=[{
            "id": bakery_id,  # bakery_id를 Qdrant의 point id로 사용 (연결)
            "vector": embedding,
            "payload": {
                "bakery_id": bakery_id,
                "summary": aisummary
            }
        }]
    )

pg_conn.commit()
pg_cur.close()
pg_conn.close() 