from typing import Any
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
import shutil
from django.conf import settings
from app.models import SyncTask
import uuid
from app.tasks import syncing_task
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect
# Create your views here.


def index(request):
    context = {
        'title': 'My Django Template',
        'headline': 'Welcome to My Django Template View',
        'content': 'This is a sample content for Django Template View.',
    }
    context["tasks"] = SyncTask.objects.all()
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

def download_synced_file(request, task_id):
    # Fetch the SyncTask by its task_id
    task = get_object_or_404(SyncTask, task_id=task_id)

    # Ensure the file exists
    if task.synced_file:
        file_path = task.synced_file.path
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{task.synced_file.name}"'
        return response
    else:
        raise Http404("File not found.")
        

def delete_task(request, task_id=None):
    if task_id:
        # Delete a specific task
        task = get_object_or_404(SyncTask, task_id=task_id)
        delete_task_files(task)
        task.delete()
    else:
        # Delete all tasks
        for task in SyncTask.objects.all():
            delete_task_files(task)
            task.delete()
        clean_directories()

    # Redirect to a success page or the home page after deletion
    return redirect('index')  # Replace 'home' with your home page's name

def delete_task_files(task):
    # Helper function to delete files from the file system
    if task.audio_file:
        if os.path.isfile(task.audio_file.path):
            os.remove(task.audio_file.path)
    if task.video_file:
        if os.path.isfile(task.video_file.path):
            os.remove(task.video_file.path)
    if task.synced_file:
        if os.path.isfile(task.synced_file.path):
            os.remove(task.synced_file.path)

def clean_directories():
    # Function to clean up the directories
    directories = ['audio_files', 'video_files', 'result']
    for directory in directories:
        dir_path = os.path.join(settings.MEDIA_ROOT, directory)
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            os.makedirs(dir_path)

from django import template
from django.utils.timesince import timesince
register = template.Library()

@register.filter(name='sub')
def subtract(value, arg):
    """Subtracts the arg from value."""
    return timesince(value, arg)