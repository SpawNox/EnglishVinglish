from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DSN

engine = create_engine(DSN)
Session = sessionmaker(bind=engine)

def get_session():
    return Session()