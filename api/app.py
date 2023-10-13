import os
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from views import *
from models import db
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from extensions import celery

# load_dotenv()


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql://postgres:1234@localhost:5432/nube1")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["JWT_SECRET_KEY"] = "frase-secreta"
app.config['CELERY_BROKER_URL'] = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
app.config['CELERY_RESULT_BACKEND'] = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Initialize Celery
celery.conf.update(app.config)
celery.main = app.name


app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

cors = CORS(app, resources={r"/*": {"origins": "*"}})

api = Api(app)

api.add_resource(ViewSignInUser, "/signin")
api.add_resource(ViewLogin, "/login")
api.add_resource(ViewConverter, "/convert")
api.add_resource(ViewConverterStatus, "/convert_status/<string:task_id>")

jwt = JWTManager(app)
