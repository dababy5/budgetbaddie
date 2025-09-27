from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user")
    phone_number = models.IntegerField(max_length=10)
    bank_name = models.CharField()
    bank_accountId = models.IntegerField()
    bank_customerId = models.IntegerField()