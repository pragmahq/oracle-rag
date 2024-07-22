import os
import csv
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values
import random

load_dotenv()

# Database connection details
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


def create_tables():
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS pragma_accounts (
        id SERIAL PRIMARY KEY,
        visibility BOOLEAN,
        discord_id BIGINT,
        username VARCHAR(255) UNIQUE,
        display_name VARCHAR(255),
        points INTEGER,
        account_secret VARCHAR(255),
        bio TEXT,
        works TEXT,
        embedding vector(1536)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS domains (
        id SERIAL PRIMARY KEY,
        account_id INTEGER REFERENCES pragma_accounts(id),
        domain_id VARCHAR(255),
        name VARCHAR(255)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS social_links (
        id SERIAL PRIMARY KEY,
        account_id INTEGER REFERENCES pragma_accounts(id),
        username VARCHAR(255),
        type VARCHAR(255),
        label VARCHAR(255),
        link VARCHAR(255)
    )
    """)

    conn.commit()
    cur.close()
    conn.close()


def read_csv_data(filename):
    with open(filename, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return list(reader)


def insert_sample_data():
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    cur = conn.cursor()

    csv_data = read_csv_data('sample_dataset.csv')

    for account in csv_data:
        # Generate random values for fields not in CSV
        visibility = random.choice([True, False])
        discord_id = random.randint(100000000000000000, 999999999999999999)
        account_secret = f"secret{random.randint(1000, 9999)}"

        cur.execute("""
        INSERT INTO pragma_accounts (visibility, discord_id, username, display_name, points, account_secret, bio, works)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """, (visibility, discord_id, account['username'], account['display_name'], int(account['points']),
              account_secret, account['bio'], account['works']))

        account_id = cur.fetchone()[0]

        # Insert domain
        execute_values(cur, """
        INSERT INTO domains (account_id, domain_id, name)
        VALUES %s
        """, [(account_id, f"domain{account_id}", account['domain'])])

        # Insert social link
        execute_values(cur, """
        INSERT INTO social_links (account_id, username, type, label, link)
        VALUES %s
        """, [(account_id, account['username'], account['social_type'], account['social_type'], account['social_link'])])

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    create_tables()
    insert_sample_data()
    print("Sample data inserted successfully.")
