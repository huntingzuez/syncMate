from django.db import models

# Create your models here.
import uuid
import os
from django.urls import reverse
from datetime import timedelta, datetime

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
    synced_file = models.FileField(upload_to='result/')
    cloudinary_path = models.CharField(max_length=225, null=True, blank=True)
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
        if self.cloudinary_path:
            return self.cloudinary_path
        relative_url = reverse('download_synced_file', kwargs={'task_id': self.task_id})
        url = "http://localhost:8000{}".format(relative_url)
        return url if self.synced_file else None
    
    @property
    def duration(self):
        self.updated_at = datetime.now() if not self.updated_at else self.updated_at 
        delta = self.updated_at - self.created_at
        print(self.created_at)
        print(delta)
        print('--------------------------')
        if  self.created_at:
            # Formatting duration as days, hours, minutes
            return str(delta - timedelta(microseconds=delta.microseconds))
        return None