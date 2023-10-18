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

    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    task_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer(), ForeignKey('user.id'), nullable=False)
    input_path: Mapped[str] = mapped_column(String(255), nullable=False)
    output_path: Mapped[str] = mapped_column(String(255), nullable=False)
    conversion_type: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[int] = mapped_column(Enum(TaskStatus), default=TaskStatus.PENDING)
    timestamp: Mapped[datetime] = mapped_column(DateTime(), default=datetime.utcnow)
    error_message: Mapped[str] = mapped_column(Text())


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    username: Mapped[str] = mapped_column(String(128))
    email: Mapped[str] = mapped_column(String(50))
    password: Mapped[str] = mapped_column(String(50))