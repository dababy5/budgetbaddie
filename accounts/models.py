from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone_number = models.IntegerField(max_length=10)
    bank_name = models.CharField(blank=True)
    bank_accountId = models.CharField(default=0)
    bank_customerId = models.CharField(default=0)

class ItemPurchaseHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="item_purchase_history")
    purchase_type = models.CharField()
    merchant_id = models.CharField()
    purchase_date = models.DateField()
    amount = models.CharField()
    description = models.CharField()