from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = 'postgresql://faramade:I1298R4emEhtKC5kkJi5qBffxHmkYYUC@dpg-d3ibmummcj7s73942b40-a.oregon-postgres.render.com/faramadeproject'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()

