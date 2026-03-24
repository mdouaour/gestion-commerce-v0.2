from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv('DB_NAME', 'pos_local.db')
DATABASE_URL = f'sqlite:///{DB_NAME}'

engine = create_engine(
    DATABASE_URL, 
    connect_args={'check_same_thread': False}, # Needed for SQLite with multi-threading
    echo=False
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
