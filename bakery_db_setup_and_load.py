import pandas as pd
import psycopg2
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

PG_DB = 'bready_for_suwon'
PG_USER = os.getenv('PG_USER')
PG_PW = os.getenv('PG_PW')
PG_HOST = 'localhost'
PG_PORT = 5432
QDRANT_HOST = 'localhost'
QDRANT_PORT = 6333

SCHEMA_NAME = 'bakery'
COLLECTION_NAME = 'bakery_summaries'
VECTOR_SIZE = 768

# 1. PostgreSQL bakery 스키마 및 테이블 생성
create_schema_sql = f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME};"
create_table_sql = f'''
CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.bakery (
    id VARCHAR(32) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    rating FLOAT,
    address VARCHAR(512)
);
'''

pg_conn = psycopg2.connect(
    dbname=PG_DB, user=PG_USER, password=PG_PW, host=PG_HOST, port=PG_PORT
)
pg_cur = pg_conn.cursor()
pg_cur.execute(create_schema_sql)
pg_cur.execute(create_table_sql)
pg_conn.commit()

# 2. Qdrant 컬렉션 생성
qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
qdrant.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config={"size": VECTOR_SIZE, "distance": "Cosine"},
)

# 3. bakery_list.csv 데이터 적재
model = SentenceTransformer('jhgan/ko-sroberta-multitask')
df = pd.read_csv('bakery_list.csv')

for _, row in df.iterrows():
    bakery_id = str(row['id'])
    name = row['name']
    rating = float(row['rating']) if not pd.isnull(row['rating']) else None
    address = row['address']
    aisummary = row['aisummary']

    # RDB에 저장 (스키마명 명시)
    pg_cur.execute(
        f"INSERT INTO {SCHEMA_NAME}.bakery (id, name, rating, address) VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
        (bakery_id, name, rating, address)
    )

    # 임베딩 생성 및 Qdrant에 저장
    embedding = model.encode(aisummary).tolist()
    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=[{
            "id": bakery_id,
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