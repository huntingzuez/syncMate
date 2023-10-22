from celery import shared_task
from syncMate.celery import app
from app.utils.inference import VideoProcessor

@app.task(bind=True, max_retries=0)
def syncing_task(self, task_id):
    try:
        main = VideoProcessor(task_id=task_id)
        main.main()
    except Exception as e:
        pass
    return True
            
            
    