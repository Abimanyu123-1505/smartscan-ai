"""
Database layer for DFIOP.

Phase 1 uses SQLite for both the relational case database and, via FTS5,
the full-text evidence index. This mirrors the roadmap's plan to start on
SQLite (FTS) and later upgrade to Elasticsearch/OpenSearch + Neo4j in
Phase 2/3 without changing the parser/plugin contract (see app/plugins/base.py).
"""
import os
import sqlite3
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "case_database.sqlite3")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    # Evidence integrity: enforce FK constraints, use WAL for durability
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_raw_connection() -> sqlite3.Connection:
    """Raw DB-API connection, used for FTS5 virtual table operations that
    SQLAlchemy's ORM does not model well. WAL mode + a busy timeout let
    this coexist with the SQLAlchemy engine's own open connections
    instead of raising 'database is locked'."""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    return conn


def init_fts_index():
    """Create the full-text index over extracted artifacts (Timeline &
    Search deliverable, Phase 1)."""
    conn = get_raw_connection()
    conn.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS artifact_index USING fts5(
            artifact_id UNINDEXED,
            case_id UNINDEXED,
            artifact_type,
            name,
            content,
            path
        )
        """
    )
    conn.commit()
    conn.close()
