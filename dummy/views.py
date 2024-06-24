from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from django.conf import settings
from subprocess import run, PIPE
from pathlib import Path
import json
from .serializers import *
class CreateProjectView(CreateAPIView):
    serializer_class = ProjectSerializer

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
        


    