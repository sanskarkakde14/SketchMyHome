from django.db import models
from django.contrib.auth import get_user_model
from .models import *
class Project(models.Model):
    project_name = models.CharField(max_length=255)
    width = models.IntegerField()
    length = models.IntegerField()
    bedroom = models.IntegerField()
    bathroom = models.IntegerField()
    car = models.IntegerField()
    temple = models.IntegerField()
    garden = models.IntegerField()
    living_room = models.IntegerField()
    store_room = models.IntegerField()

    def __str__(self):
        return self.project_name



class UserPDF(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    pdf = models.FileField(upload_to='pdfs/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} - {self.pdf.name}"
    

