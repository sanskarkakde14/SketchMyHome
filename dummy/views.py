from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from django.conf import settings
from subprocess import run, PIPE
from django.http import HttpResponse
from pathlib import Path
import json, os
from rest_framework.permissions import IsAuthenticated
from django.core.files import File
from urllib.parse import urljoin
from .serializers import *

class CreateProjectView(CreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            user = request.user
            return self.run_external_script(serializer.validated_data, user)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def run_external_script(self, data, user):
        script_path = settings.BASE_DIR / 'dummy' / 'DXFLogic.py'

        if not script_path.exists():
            return Response({'message': 'Error: Script path does not exist'}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Convert serializer data to JSON string
        json_data = json.dumps(data)

        # Pass the JSON data as a command-line argument
        result = run(['python', str(script_path), json_data], stdout=PIPE, stderr=PIPE, text=True)

        if result.returncode == 0:
            output_data = result.stdout.strip()
            pdf_filepaths = self.extract_pdf_filepaths(output_data)
            if pdf_filepaths:
                self.move_pdfs_to_media(pdf_filepaths, user)
                return Response({
                    'message': 'External script executed successfully and PDFs moved',
                    'output': result.stdout
                })
            else:
                return Response({
                    'message': 'External script executed successfully but no PDF filenames returned',
                    'output': result.stdout
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                'message': 'Error running external script',
                'error': result.stderr
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def extract_pdf_filepaths(self, output_data):
        # Assuming the script returns a list of file paths in a string format like:
        # "PDFs generated successfully: ['/path/to/pdf1.pdf', '/path/to/pdf2.pdf']"
        try:
            start = output_data.index('[')
            end = output_data.index(']') + 1
            pdf_filepaths = json.loads(output_data[start:end].replace("'", '"'))
            return pdf_filepaths
        except (ValueError, IndexError, json.JSONDecodeError) as e:
            return []

    def move_pdfs_to_media(self, pdf_filepaths, user):
        for source_path in pdf_filepaths:
            if os.path.exists(source_path):
                pdf_filename = os.path.basename(source_path)
                destination_path = os.path.join(settings.MEDIA_ROOT, 'pdfs', pdf_filename)
                os.makedirs(os.path.dirname(destination_path), exist_ok=True)

                with open(source_path, 'rb') as f:
                    django_file = File(f)
                    user_pdf = UserPDF(user=user)
                    user_pdf.pdf.save(pdf_filename, django_file, save=True)

                os.remove(source_path)  # Remove the file from the source folder if needed
            else:
                raise FileNotFoundError(f"PDF not found in source folder: {source_path}")

class PDFListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_pdfs = UserPDF.objects.all()
        serializer = PDFSerializer(user_pdfs, many=True)
        return Response(serializer.data)

class PDFServeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, filename):
        pdf_folder = os.path.join(settings.MEDIA_ROOT, 'pdfs')
        file_path = os.path.join(pdf_folder, filename)

        # Debug: Print the file path
        print(f"Looking for file at: {file_path}")

        if os.path.exists(file_path):
            print(f"File found: {file_path}")  # Debug: Confirm file exists
            with open(file_path, 'rb') as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename="{filename}"'
                return response
        else:
            print(f"File not found: {file_path}")  # Debug: Log file not found
            return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)