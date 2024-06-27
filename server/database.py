from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi import Depends

from typing import Annotated
from datetime import datetime

Base = declarative_base()

class Logs(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String)
    response = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Criticals(Base):
    __tablename__ = 'criticals'

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    error_message = Column(String, nullable=False)
    traceback = Column(String, nullable=False)

class CriticalsCreate(BaseModel):
    error_message: str
    traceback: str

engine = create_engine("postgresql://chatbot_47wg_user:qTKp526t71BRQq149XWxDytbotK1Sn50@dpg-cn7inv821fec73fm3lmg-a.oregon-postgres.render.com/chatbot_47wg") # postgresql://postgres:123@localhost/chatbot
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]