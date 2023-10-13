import hashlib
import os
import requests
from flask_restful import Resource
from flask import request, abort
from models import db, User, UserSchema, VideoConversionTask, VideoConversionTaskSchema, TaskStatus
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from extensions import celery
from celery.result import AsyncResult

CONVERTER_SERVICE_URL = os.environ.get('CONVERTER_SERVICE_URL', 'http://localhost:5001')


def initiate_conversion_with_service(input_path, output_path, conversion_type):
    task = celery.send_task('tasks.convert_video', args=[input_path, output_path, conversion_type])
    print(task)

    return {
        'status': 'Conversion started',
        'task_id': str(task.id)
    }


class ViewSignInUser(Resource):
    def post(self):
        user = User.query.filter(
            User.username == request.json["username"]
        ).first()

        if user is not None:
            return {"mensaje": "usuario ya existe", 'status': 400}

        if request.json["password1"] != request.json["password2"]:
            return {"mensaje": "password no coinciden", 'status': 400}

        encrypted_password = hashlib.md5(
            request.json["password1"].encode("utf-8")
        ).hexdigest()

        new_user = User(
            username=request.json["username"],
            email=request.json["email"],
            password=encrypted_password
        )
        db.session.add(new_user)
        db.session.commit()

        return {"message": "usuario creado exitosamente", "id": new_user.id}, 201


class ViewLogin(Resource):
    def post(self):
        encrypted_password = hashlib.md5(
            request.json["password"].encode("utf-8")
        ).hexdigest()
        user = User.query.filter(
            User.username == request.json["username"],
            User.password == encrypted_password,
        ).first()

        if user is None:
            return "El usuario no existe", 404

        access_token = create_access_token(identity=user.id)
        return {
            "message": "Inicio de sesión exitoso",
            "token": access_token,
            "id": user.id,
        }, 200


class ViewConverter(Resource):
    @jwt_required()
    def post(self):
        data = request.json
        input_path = data['input_path']
        output_path = data['output_path']
        conversion_type = data['conversion_type']

        try:
            converter_response = initiate_conversion_with_service(input_path, output_path, conversion_type)
            task_id = converter_response['task_id']
            print(task_id)

            # Create an entry in the VideoConversionTask table
            task_entry = VideoConversionTask(
                task_id=task_id,
                user_id=get_jwt_identity(),
                input_path=input_path,
                output_path=output_path,
                conversion_type=conversion_type,
                status=TaskStatus.PENDING
            )
            db.session.add(task_entry)
            db.session.commit()

            return {"message": "Conversion started", "task_id": task_id}, 202

        except Exception as e:
            return {"error": str(e)}, 500


class ViewConverterStatus(Resource):
    def get(self, task_id):
        task = AsyncResult(task_id, app=celery)
        response = {
            'state': task.state
        }

        # Handle custom task result based on state
        if task.state == 'SUCCESS':
            response['result'] = str(task.result)  # Convert result to string if not serializable
        elif task.state == 'FAILURE':
            response['error_message'] = str(task.result)  # Convert Exception to string

        # Update database record
        task_entry = VideoConversionTask.query.filter_by(task_id=task_id).first()
        if not task_entry:
            abort(404, description="Task not found")  # Return a 404 error if task is not found

        task_entry.status = task.state  # Or map this to your own statuses if required

        if 'error_message' in response:
            task_entry.error_message = response['error_message']

        db.session.commit()

        return response
