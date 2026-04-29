import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

# Load .env if it exists (for local dev), otherwise ignore (for GitHub Actions)
load_dotenv()

def get_db_connection():
    # It is safer to use os.environ.get() to avoid errors if a variable is missing
    return psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        port=os.environ.get("DB_PORT", "5432")
    )

def fetch_data(query_path='sql/feature_query.sql'):
    base_path = os.path.dirname(os.path.dirname(__file__)) # Go up to repo root
    absolute_sql_path = os.path.join(base_path, query_path)
    
    conn = get_db_connection()
    try:
        with open(absolute_sql_path, 'r') as f:
            query = f.read()
        
        df = pd.read_sql(query, conn)
        return df
    finally:
        conn.close()
