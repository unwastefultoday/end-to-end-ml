import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )

def fetch_data(query_path='sql/feature_query.sql'):
    conn = get_db_connection()
    with open(query_path, 'r') as f:
        query = f.read()
    df = pd.read_sql(query, conn)
    conn.close()
    return df
