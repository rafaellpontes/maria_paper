from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import json

with open('config.json') as f:
    data = json.load(f)

host = data['database']['host']
port = data['database']['port']
database = data['database']['database']
username = data['database']['username']
password = data['database']['password']

SQLALCHEMY_DATABASE_URL = f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = Session()
    try:
        return db
    finally:
        db.close()

def get_engine():
    return engine