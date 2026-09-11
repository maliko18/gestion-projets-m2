import os
import sqlite3
from dotenv import load_dotenv

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

load_dotenv()

USE_SQLITE = os.getenv("USE_SQLITE", "false").lower() in ("true", "1", "yes")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "gestion_projets")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

SQLITE_DB_PATH = "projets.db"


def get_db_connection():
    """
    Retourne une connexion active à la base de données (PostgreSQL ou SQLite en fallback).
    En PostgreSQL, retourne un curseur sous forme de dictionnaire (RealDictCursor).
    """
    if USE_SQLITE or not HAS_PSYCOPG2:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn, "sqlite"

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            cursor_factory=RealDictCursor
        )
        return conn, "postgres"
    except Exception as e:
        print(f"[ATTENTION] Impossible de se connecter à PostgreSQL ({e}).")
        print("[INFO] Bascule automatique sur SQLite pour le développement local.")
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn, "sqlite"
