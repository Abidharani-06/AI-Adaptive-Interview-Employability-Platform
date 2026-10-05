import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Configurable database URL (defaults to SQLite, easily switched to PostgreSQL via DATABASE_URL env var)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./platform.db")

# SQLite requires check_same_thread=False for multi-threaded FastAPI handlers
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency that yields an isolated database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initializes database schema and performs safe migrations for new columns.
    """
    Base.metadata.create_all(bind=engine)

    # Safe migration for SQLite to ensure new columns exist without breaking existing databases
    if DATABASE_URL.startswith("sqlite"):
        import sqlite3
        db_path = DATABASE_URL.replace("sqlite:///", "")
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            try:
                # Check user table columns
                cursor.execute("PRAGMA table_info(users)")
                existing_cols = [row[1] for row in cursor.fetchall()]

                columns_to_add = [
                    ("is_verified", "BOOLEAN DEFAULT 0"),
                    ("otp_hash", "VARCHAR(255)"),
                    ("otp_expires_at", "DATETIME"),
                    ("otp_attempts", "INTEGER DEFAULT 0"),
                    ("resend_cooldown_until", "DATETIME"),
                    ("gender", "VARCHAR(50)"),
                    ("dob", "VARCHAR(50)"),
                    ("year_of_study", "VARCHAR(50)"),
                    ("city", "VARCHAR(100)")
                ]

                for col_name, col_def in columns_to_add:
                    if col_name not in existing_cols:
                        cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_def}")
                        print(f"[DB MIGRATION] Added column '{col_name}' to 'users' table.")

                # Ensure existing users are verified so previous test users are not locked out
                cursor.execute("UPDATE users SET is_verified = 1 WHERE is_verified IS NULL OR is_verified = 0")
                conn.commit()
            except Exception as e:
                print(f"[DB MIGRATION WARNING] Migration check: {e}")
            finally:
                conn.close()

