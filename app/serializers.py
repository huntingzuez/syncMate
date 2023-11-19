from rest_framework import serializers
from app.models import SyncTask
from django.core.exceptions import ValidationError
import os

def validate_audio_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # Extract the file extension
    if ext.lower() != '.wav':
        raise serializers.ValidationError("Audio file must be a .wav file")

def validate_video_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # Extract the file extension
    if ext.lower() != '.mp4':
        raise serializers.ValidationError("Video file must be a .mp4 file")

class FileUploadSerializer(serializers.Serializer):
    videoFile = serializers.FileField(validators=[validate_video_file_extension])
    audioFile = serializers.FileField(validators=[validate_audio_file_extension])

class SyncTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncTask
        fields = ('task_id', 'input_audio_file', 'input_video_file', 'result_synced_file', 'status', 'created_at', 'updated_at')