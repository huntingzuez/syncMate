from rest_framework import serializers
from app.models import SyncTask

class FileUploadSerializer(serializers.Serializer):
    videoFile = serializers.FileField()
    audioFile = serializers.FileField()

class SyncTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncTask
        fields = ('task_id', 'input_audio_file', 'input_video_file', 'result_synced_file', 'status', 'created_at', 'updated_at')