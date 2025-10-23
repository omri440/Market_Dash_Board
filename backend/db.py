from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
import sys
import dotenv

dotenv.load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))
Base = declarative_base()
Session = sessionmaker(bind=engine,autocommit=False, autoflush=False)

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

