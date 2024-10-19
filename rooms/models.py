from django.db import models



# Model representing a room
class Room(models.Model):
    room_name = models.CharField(max_length=50)  # Room name with a maximum length of 50 characters
    room_capacity = models.IntegerField()  # Room capacity as an integer
    projector_available = models.BooleanField(default=False)  # Boolean field to indicate if a projector is available

    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the room was created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for when the room was last updated

    # String representation of the room object
    def __str__(self):
        return self.room_name  # Return the room name as its string representation

    # Override the save method (optional customization)
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)  # Call the parent class's save method


# Model representing a reservation for a room
class Reservation(models.Model):
    date = models.DateField()  # Reservation date as a date field
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reservations')  # Foreign key linking to Room model
    comment = models.TextField(null=True)  # Optional comment field for the reservation

    class Meta:
        unique_together = ('room', 'date')  # Ensure a room cannot have more than one reservation on the same date

