from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone_number = models.IntegerField()
    bank_name = models.CharField(blank=True)
    bank_accountId = models.CharField(default=0)
    bank_customerId = models.CharField(default=0)

class ItemPurchaseHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="item_purchase_history")
    purchase_type = models.CharField()
    merchant_id = models.CharField()
    purchase_date = models.DateField()
    amount = models.DecimalField(decimal_places=2, max_digits=30)
    description = models.CharField()

class BudgetPlan(models.Model):
    BUDGET_TYPE_CHOICES = [
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
        ("custom", "Custom Range"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="budget_plans")
    plan_name = models.CharField(max_length=255)
    budget_type = models.CharField(max_length=20, choices=BUDGET_TYPE_CHOICES, default="weekly")
    budget_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Only used if budget_type == "custom"
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    accept_sms = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.plan_name} ({self.user.username}) - {self.budget_type}"