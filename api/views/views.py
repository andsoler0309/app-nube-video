import hashlib
import os
from flask_restful import Resource
from flask import request, abort, current_app, send_from_directory
from models import db, User, UserSchema, VideoConversionTask, VideoConversionTaskSchema, TaskStatus
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from extensions import celery
from celery.result import AsyncResult
from werkzeug.utils import secure_filename

tasks_schema = VideoConversionTaskSchema(many=True)
task_schema = VideoConversionTaskSchema()

def ensure_directories_exists(directories):
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

def initiate_conversion_with_service(input_path, output_path, conversion_type):
    task = celery.send_task('tasks.convert_video', args=[input_path, output_path, conversion_type])
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
        if 'file' not in request.files:
            return {'error': 'No file part'}, 400

        file = request.files['file']
        if file.filename == '' or not file:
            return {'error': 'No selected file'}, 400

        filename = secure_filename(file.filename)
        file_basename, file_extension = os.path.splitext(filename)

        user_upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], str(get_jwt_identity()))
        user_output_path = os.path.join(current_app.config['CONVERTED_FOLDER'], str(get_jwt_identity()))
        ensure_directories_exists([user_upload_path, user_output_path])

        filepath = os.path.join(user_upload_path, filename)
        file.save(filepath)

        conversion_type = request.form.get('conversion_type')
        input_path = filepath
        output_path = os.path.join(user_output_path, f"converted_{file_basename}")
        try:
            converter_response = initiate_conversion_with_service(input_path, output_path, conversion_type)
            task_id = converter_response['task_id']

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

    @jwt_required()
    def get(self):
        order = request.args.get('order')
        max_results = request.args.get('max')
        user_id = get_jwt_identity()

        tasks_query = VideoConversionTask.query.filter_by(user_id=user_id)

        if order == '1':
            tasks_query = tasks_query.order_by(VideoConversionTask.id.desc())
        else:
            tasks_query = tasks_query.order_by(VideoConversionTask.id.asc())

        if max_results:
            tasks_query = tasks_query.limit(int(max_results))

        tasks = tasks_query.all()
        return {"tasks": tasks_schema.dump(tasks)}, 200


class ViewConverterStatus(Resource):
    @jwt_required()
    def get(self, task_id):
        task = VideoConversionTask.query.filter_by(task_id=task_id).first()
        if not task:
            return {"error": "Task not found"}, 404

        if task.user_id != get_jwt_identity():
            return {"error": "Not authorized to view this task"}, 403

        return {"task": task_schema.dump(task)}, 200

    @jwt_required()
    def delete(self, task_id):
        try:
            task = VideoConversionTask.query.filter_by(task_id=task_id).first()
            if not task:
                return {"error": "Task not found"}, 404

            if task.user_id != get_jwt_identity():
                return {"error": "Not authorized to delete this task"}, 403

            db.session.delete(task)
            db.session.commit()
            return {}, 204

        except Exception as e:
            return {"error": str(e)}, 500


class ViewFileDownload(Resource):
    @jwt_required()
    def get(self):
        task_id = request.args.get('task_id')
        if not task_id:
            return {'error': 'Task id is required'}, 400

        try:
            task = VideoConversionTask.query.filter_by(task_id=task_id).first()
            if not task:
                return {"error": "Task not found"}, 404

            if task.user_id != get_jwt_identity():
                return {"error": "Not authorized to download this file"}, 403

            if task.status != TaskStatus.SUCCESS:
                return {"error": "File is not ready for download"}, 400

            filepath = task.output_path + '.' + task.conversion_type
            directory, filename = os.path.split(filepath)
            return send_from_directory(directory, filename, as_attachment=True)
        except FileNotFoundError:
            return {'error': 'file not found'}, 404
