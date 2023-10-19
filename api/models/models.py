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
    broker_task_id = db.Column(db.String(255), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    input_path = db.Column(db.String(255), nullable=False)
    output_path = db.Column(db.String(255), nullable=False)
    conversion_type = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.PENDING)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    error_message = db.Column(db.Text)


class VideoConversionTaskSchema(SQLAlchemyAutoSchema):
    status = fields.Method("get_status_as_string")

    class Meta:
        model = VideoConversionTask
        include_relationships = True
        load_instance = True
        fields = ("id", "conversion_type", "status")

    def get_status_as_string(self, obj):
        return obj.status.value
