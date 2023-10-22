from django.contrib import admin
from django.urls import include, path
from app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.FileUploadView.as_view(), name='file_upload'),
    path('api/upload/', views.FileUploadAPIView.as_view(), name='api_file_upload'),
    path('api/sync/<uuid:task_id>/status/', views.SyncTaskAPIView.as_view(), name='api_sync_task_status'),
    path('download/<uuid:task_id>/', views.download_synced_file, name='download_synced_file'),
]
