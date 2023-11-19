from django import forms
from django.core.exceptions import ValidationError
import os 

class FileUploadForm(forms.Form):
    videoFile = forms.FileField(allow_empty_file=False, label='Upload Video File', required=True)
    audioFile = forms.FileField(allow_empty_file=False, label='Upload Audio File', required=True)

    def clean_audioFile(self):
        audio_file = self.cleaned_data['audioFile']
        ext = os.path.splitext(audio_file.name)[1]  # Extract the file extension
        if ext.lower() != '.wav':
            raise ValidationError("Audio file must be a .wav file")
        return audio_file

    def clean_videoFile(self):
        video_file = self.cleaned_data['videoFile']
        ext = os.path.splitext(video_file.name)[1]  # Extract the file extension
        if ext.lower() != '.mp4':
            raise ValidationError("Video file must be a .mp4 file")
        return video_file