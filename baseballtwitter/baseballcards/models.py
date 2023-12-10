from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phoneNumber = models.CharField(max_length=20)

class Card(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, db_index=True)
    team = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, db_index=True)
    condition = models.CharField(max_length=10, choices=[
        ('Mint', 'Mint'),
        ('Excellent', 'Excellent'),
        ('Great', 'Great'),
        ('Good', 'Good'),
        ('Fair', 'Fair'),
        ('Poor', 'Poor'),
        ('N/A', 'N/A')
    ], default='N/A', db_index=True)
    numLikes = models.IntegerField(default=0)
    numDislikes = models.IntegerField(default=0)