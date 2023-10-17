from django import forms

class FileUploadForm(forms.Form):
    videoFile = forms.FileField(allow_empty_file=False, label='Upload Video File', required=True)
    audioFile = forms.FileField(allow_empty_file=False, label='Upload Audio File', required=True)
