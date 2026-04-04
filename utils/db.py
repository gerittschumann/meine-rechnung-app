import psycopg2
import psycopg2.extras
import os

def get_connection():
    return psycopg2.connect(
        host=os.getenv("PGHOST"),
        database=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        port=os.getenv("PGPORT"),
        cursor_factory=psycopg2.extras.RealDictCursor
    )
