from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from django.conf import settings
from subprocess import run, PIPE
from django.http import FileResponse, HttpResponse
from pathlib import Path
import json,os
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from urllib.parse import urljoin

class CreateProjectView(CreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return self.run_external_script(serializer.validated_data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def run_external_script(self, data):
        script_path = settings.BASE_DIR / 'dummy' / 'DXFLogic.py'
        
        if not script_path.exists():
            return Response({'message': 'Error: Script path does not exist'}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Convert serializer data to JSON string
        json_data = json.dumps(data)

        # Pass the JSON data as a command-line argument
        result = run(['python', str(script_path), json_data], stdout=PIPE, stderr=PIPE, text=True)

        if result.returncode == 0:
            return Response({
                'message': 'External script executed successfully',
                'output': result.stdout
            })
        else:
            return Response({
                'message': 'Error running external script',
                'error': result.stderr
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


    


#Damn
class PDFListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        pdf_folder = os.path.join(settings.BASE_DIR, 'dummy', 'pdf')
        pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
        
        base_url = request.build_absolute_uri('/')[:-1]  # Remove trailing slash
        pdf_list = [
            {
                'name': pdf_file,
                'url': urljoin(base_url, f'/api/pdf/{pdf_file}')
            }
            for pdf_file in pdf_files
        ]
        
        serializer = PDFSerializer(pdf_list, many=True)
        return Response(serializer.data)

class PDFServeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, filename):
        pdf_folder = os.path.join(settings.BASE_DIR, 'dummy', 'pdf')
        file_path = os.path.join(pdf_folder, filename)
        
        if os.path.exists(file_path):
            with open(file_path, 'rb') as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename="{filename}"'
                return response
        else:
            return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)
        
















