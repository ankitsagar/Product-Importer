from rest_framework.generics import CreateAPIView
# DRF Imports
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

# App Imports
from .serializers import FileUploadSerializer

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
            {"message": "upload successful"},
            status=status.HTTP_202_ACCEPTED
        )
