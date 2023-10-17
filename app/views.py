from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from app.forms import FileUploadForm
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from app.serializers import FileUploadSerializer, SyncTaskSerializer
from django.http import JsonResponse
import os
from django.conf import settings
from app.models import SyncTask
import uuid
from app.utils.inference import VideoProcessor
from app.tasks import syncing_task

# Create your views here.


def index(request):
    context = {
        'title': 'My Django Template',
        'headline': 'Welcome to My Django Template View',
        'content': 'This is a sample content for Django Template View.',
    }
    return render(request, 'index.html', context)

class FileUploadView(FormView):
    template_name = 'index.html'
    form_class = FileUploadForm
    success_url = reverse_lazy('index')  # replace with the URL of your choice

    def form_valid(self, form):
        # Handle file upload here
        # Example: save the files to the server, process them, etc.
        # You have access to the files with form.cleaned_data['videoFile'] and form.cleaned_data['audioFile']
        sync_task = SyncTask()
        sync_task.task_id = uuid.uuid4()
        sync_task.audio_file = form.cleaned_data['audioFile']
        sync_task.video_file = form.cleaned_data['videoFile']
        sync_task.save()
        syncing_task.delay(sync_task.task_id)
        return super().form_valid(form)
    

class FileUploadAPIView(APIView):
    serializer_class = FileUploadSerializer

    def post(self, request, *args, **kwargs):
        file_serializer = FileUploadSerializer(data=request.data)
        if file_serializer.is_valid():
            sync_task = SyncTask()
            sync_task.task_id = uuid.uuid4()
            sync_task.audio_file = file_serializer.validated_data['audioFile']
            sync_task.video_file = file_serializer.validated_data['videoFile']
            sync_task.save()
            syncing_task.delay(sync_task.task_id)
            serializer = SyncTaskSerializer(sync_task)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SyncTaskAPIView(APIView):
    serializer_class = SyncTaskSerializer

    def get(self, request, *args, **kwargs):
        task_id = self.kwargs['task_id']
        try:
            task = SyncTask.objects.get(task_id=task_id)
            serializer = SyncTaskSerializer(task)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SyncTask.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)