from django.db import models

# Create your models here.
import uuid
import os

class SyncTask(models.Model):

    started = 1
    failed = 2
    finished = 3
    status_choices = (
        
        (started, "Started"),
        (failed, "Failed"),
        (finished, "Finihsed"),
    )
    audio_file = models.FileField(upload_to='audio_files/')
    video_file = models.FileField(upload_to='video_files/')
    synced_file_path = models.CharField(max_length=255, blank=True, null=True)
    task_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    status = models.IntegerField(choices=status_choices, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def input_audio_file(self):
        return "{}{}".format(os.getenv("API_URL", "http://localhost:8000"), str(self.audio_file)) if self.audio_file else None
    
    @property
    def input_video_file(self):
        return "{}{}".format(os.getenv("API_URL", "http://localhost:8000"), str(self.video_file)) if self.video_file else None

    @property
    def result_synced_file(self):
        return "{}{}".format(os.getenv("API_URL", "http://localhost:8000"), str(self.synced_file_path)) if self.synced_file_path else None