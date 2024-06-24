from django.urls import path
from .views import CreateProjectView

urlpatterns = [
    path('create-project/', CreateProjectView.as_view(), name='create-project'),
]