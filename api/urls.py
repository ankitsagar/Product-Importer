from django.urls import path

from .views import FileUpload, GetProgress, GetUploadURL

app_name = "api"

urlpatterns = [
    path('file-upload/', FileUpload.as_view(), name="file_upload"),
    path('get-upload-url/', GetUploadURL.as_view(), name="get_upload_url"),
    path(
        'get-import-progress/<str:task_id>/',
        GetProgress.as_view(),
        name="get_progress"
    ),
]
