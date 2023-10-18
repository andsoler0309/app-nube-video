import os
from celery.exceptions import Ignore
from utils import get_conversion_command
from celery_worker import celery_app
from celery import states
import db


@celery_app.task(bind=True)
def convert_video(self, input_path, output_path, conversion_type, task_id):
    self.update_state(state=states.STARTED, meta={'status': 'Converting...'})
    cmd = get_conversion_command(input_path, output_path, conversion_type)

    with db.session() as session:
        task = session.query(db.VideoConversionTask).filter(
            db.VideoConversionTask.id == task_id
        ).first()
        task.status = db.TaskStatus.STARTED
        task.broker_task_id = self.request.id
        session.commit()

        if cmd:
            os.system(cmd)
            self.update_state(state=states.SUCCESS, meta={'status': f'File saved to {output_path}'})
            task.status = db.TaskStatus.SUCCESS
            session.commit()
            return f"File converted and saved to {output_path}"
        else:
            self.update_state(state=states.FAILURE, meta={'status': 'Invalid conversion type'})
            task.status = db.TaskStatus.FAILURE
            task.error_message = 'Invalid conversion type'
            session.commit()
            raise Ignore()
