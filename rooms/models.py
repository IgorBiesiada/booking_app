from django.db import models



class Room(models.Model):
    room_name = models.CharField(max_length=50)
    room_capacity = models.IntegerField()
    projector_available = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.room_name


    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

class Reservation(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE)
    comment = models.TextField(max_length=255)

    class Meta:
        unique_together = ('room_id', 'date')

