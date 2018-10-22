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

    def remaining(self):
        allobjects= AttendConcert.objects.filter(concert=self)
        total=0
        for obj in allobjects:
            total+= obj.quantity
        return self.capacity-total


    def __str__(self):
        return self.name

class FollowedUser(models.Model):
    following=models.ForeignKey(User, default=1, related_name='following', on_delete=models.CASCADE)
    follower=models.ForeignKey(User, default=1,  related_name='follower', on_delete=models.CASCADE)

class AttendConcert(models.Model):
    concert = models.ForeignKey(Concert, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
    	return self.concert.name
