from django.urls import path

from .views import FileUpload

app_name = "api"

urlpatterns = [
    path('file-upload/', FileUpload.as_view(), name="file_upload"),
]
