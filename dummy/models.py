from django.db import models

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



