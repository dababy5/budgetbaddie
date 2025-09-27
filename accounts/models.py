from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user")
    phone_number = models.IntegerField(max_length=10)
    bank_name = models.CharField(blank=True)
    bank_accountId = models.CharField(default=0)
    bank_customerId = models.CharField(default=0)