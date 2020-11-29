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
