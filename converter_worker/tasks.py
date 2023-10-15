import os
from celery.exceptions import Ignore
from utils import get_conversion_command
from celery_worker import celery_app
from celery import states


@celery_app.task(bind=True)
def convert_video(self, input_path, output_path, conversion_type):
    self.update_state(state=states.STARTED, meta={'status': 'Converting...'})
    cmd = get_conversion_command(input_path, output_path, conversion_type)
    if cmd:
        os.system(cmd)
        self.update_state(state=states.SUCCESS, meta={'status': f'File saved to {output_path}'})
        return f"File converted and saved to {output_path}"
    else:
        self.update_state(state=states.FAILURE, meta={'status': 'Invalid conversion type'})
        raise Ignore()


