from .utils import extract_text_from_pdf
from .models import LegalDocument
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .serializers import LegalDocumentSerializer

class UploadDocumentAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = LegalDocumentSerializer(
            data=request.data
        )

        if serializer.is_valid():

            serializer.save(
                user=request.user
            )

            return Response(
                {
                    "message": "Document uploaded successfully"
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
class ExtractTextAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, document_id):

        try:

            document = LegalDocument.objects.get(
                id=document_id,
                user=request.user
            )

            extracted_text = extract_text_from_pdf(
                document.document.path
            )

            return Response({
                "document_title": document.title,
                "extracted_text": extracted_text
            })

        except LegalDocument.DoesNotExist:

            return Response(
                {
                    "error": "Document not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )