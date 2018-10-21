from django.db import models
from django.contrib.auth.models import User

class Concert(models.Model):
    organizer = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    description = models.TextField()
    start_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    concert_of = models.CharField(max_length=120)
    capacity = models.IntegerField()


    def __str__(self):
        return self.name
