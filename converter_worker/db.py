from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column, scoped_session
from datetime import datetime
import enum
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:1234@localhost:5432/nube1")

engine = create_engine(DATABASE_URL)
session = scoped_session(sessionmaker(engine))
Base = declarative_base()


class TaskStatus(enum.Enum):
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class VideoConversionTask(Base):
    __tablename__ = "video_conversion_task"

    id = Column(Integer, primary_key=True)
    broker_task_id = Column(String(255), unique=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    input_path = Column(String(255), nullable=False)
    output_path = Column(String(255), nullable=False)
    conversion_type = Column(String(255), nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    timestamp = Column(DateTime, default=datetime.utcnow)
    error_message = Column(Text)


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String(128))
    email = Column(String(50))
    password = Column(String(50))
