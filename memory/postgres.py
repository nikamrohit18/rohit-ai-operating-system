import uuid
import datetime
from sqlalchemy import create_engine, Column, String, Text, JSON, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from config import get_settings

Base = declarative_base()


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_type = Column(String, nullable=False)
    input = Column(Text, nullable=False)
    output = Column(Text)
    status = Column(String, default="pending")
    context = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class KnowledgeItem(Base):
    __tablename__ = "knowledge_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source = Column(String)
    content = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSON)
    vector_id = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


def _engine():
    return create_engine(get_settings().database_url)


def get_session() -> Session:
    return sessionmaker(bind=_engine())()


def init_db():
    Base.metadata.create_all(bind=_engine())
