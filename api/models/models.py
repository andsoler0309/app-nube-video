import enum
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128))
    email = db.Column(db.String(50))
    password = db.Column(db.String(50))


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True

class TaskStatus(enum.Enum):
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"

class VideoConversionTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(255), unique=True, nullable=False)  # The ID returned by Celery
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Assuming you want to track which user initiated the task
    input_path = db.Column(db.String(255), nullable=False)
    output_path = db.Column(db.String(255), nullable=False)
    conversion_type = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.PENDING)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    error_message = db.Column(db.Text)  # If the task fails, store the error message here

class VideoConversionTaskSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = VideoConversionTask
        include_relationships = True
        load_instance = True