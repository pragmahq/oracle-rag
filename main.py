import os
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_postgres import PGVector

import psycopg
import psycopg2
from psycopg.rows import dict_row
from psycopg2.extras import execute_values
from langchain_core.documents import Document

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

CONNECTION_STRING = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"

embeddings_model = OpenAIEmbeddings()


def get_db_connection():
    return psycopg.connect(CONNECTION_STRING, row_factory=dict_row)


def fetch_pragma_accounts(connection):
    with connection.cursor() as cur:
        cur.execute("""
        SELECT * FROM pragma_accounts
        WHERE embedding IS NULL
        LIMIT 100  -- Process in batches to avoid overwhelming the API
        """)
        return cur.fetchall()


def generate_embeddings(accounts):
    for account in accounts:
        text = f"{account['username']} {account['display_name']} {account['bio']} {account['works']}"
        embedding = embeddings_model.embed_query(text)
        yield account['id'], embedding


"dbname=test user=postgres password=secret"


def update_embeddings(account_embeddings):
    with psycopg2.connect(CONNECTION_STRING) as connection:
        with connection.cursor() as cur:
            query = """
                UPDATE pragma_accounts
                SET embedding = data.embedding
                FROM (VALUES %s) AS data (id, embedding)
                WHERE pragma_accounts.id = data.id
                """

            execute_values(
                cur,
                query,
                account_embeddings,
                template=None,
                page_size=100
            )
            connection.commit()


def process_embeddings():
    with get_db_connection() as conn:
        total_processed = 0
        while True:
            accounts = fetch_pragma_accounts(conn)
            if not accounts:
                break
            account_embeddings = list(generate_embeddings(accounts))
            update_embeddings(account_embeddings)
            total_processed += len(account_embeddings)
            print(
                f"Updated embeddings for {len(account_embeddings)} accounts. Total processed: {total_processed}")


def setup_qa_chain():
    vector_store = PGVector(
        connection=CONNECTION_STRING,
        embeddings=embeddings_model,
        collection_name="pragma_accounts",
        relevance_score_fn=lambda score: 1 - score,
    )

    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    llm = OpenAI(temperature=0)
    print(
        vector_store.similarity_search('AI', k=10, filter={
            'id': {'$in': [1, 5, 2, 9]}
        })
    )

    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever
    )


def find_similar_embeddings(query_embedding, limit=5):
    k = 5
    similarity_threshold = 0.7
    query = session.query(TextEmbedding, TextEmbedding.embedding.cosine_distance(query_embedding)
                          .label("distance"))
    .filter(TextEmbedding.embedding.cosine_distance(query_embedding) < similarity_threshold)
    .order_by("distance")
    .limit(k)
    .all()


def main():
    process_embeddings()
    qa_chain = setup_qa_chain()

    query = "Robotics"
    print("Running query:", query)

    retriever = qa_chain.retriever
    similar_docs = retriever.invoke(query)
    print(f"Number of similar documents retrieved: {len(similar_docs)}")
    for i, doc in enumerate(similar_docs):
        print(f"Document {i+1}:")
        print(doc.page_content[:200])  # Print first 200 characters
        print("---")

    # result = qa_chain.run(query)


if __name__ == "__main__":
    main()
