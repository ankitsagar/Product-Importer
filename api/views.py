# Django Import
from django.conf import settings

# DRF Imports
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

# App Imports
from .serializers import FileUploadSerializer
from product.constants import TaskStates

# Other imports
from celery.result import AsyncResult
import boto3
import time


# I have not designed user login and permission modules so all APIs are open


class FileUpload(CreateAPIView):
    serializer_class = FileUploadSerializer
    parser_classes = [MultiPartParser]
    permission_classes = []
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "upload successful", "task_id": serializer.task_id},
            status=status.HTTP_202_ACCEPTED
        )


class GetProgress(RetrieveAPIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request, task_id, *args, **kwargs):
        result = AsyncResult(task_id)
        # We don't need internal error message to show up in client side.
        if result.state == TaskStates.FAILURE:
            details = {"message": "Invalid File Uploaded"}
        else:
            details = result.info

        return Response({"state": result.state, "details": details})


class GetUploadURL(RetrieveAPIView):

    def get(self, request, **kwargs):
        filename = request.query_params.get("filename")
        if filename:
            filename = "tmp/" + filename
        else:
            filename = "tmp/" + str(time.time()) + ".csv"
        s3 = boto3.client(
            's3',
            region_name=settings.AWS_S3_REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        bucket = settings.AWS_STORAGE_BUCKET_NAME

        return Response(
            s3.generate_presigned_post(
                Bucket=bucket,
                Key=filename,
                Fields={},
                Conditions=[],
                ExpiresIn=3600
            )
        )
