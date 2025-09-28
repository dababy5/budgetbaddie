from django.contrib import admin
from .models import Profile,ItemPurchaseHistory,BudgetPlan

# Register your models here

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone_number", "bank_name", "bank_accountId", "bank_customerId")

@admin.register(ItemPurchaseHistory)
class ItemPurchaseHistoryAdmin(admin.ModelAdmin):
    list_display = ("user", "merchant_id", "purchase_date", "amount", "description")

@admin.register(BudgetPlan)
class BudgetPlanAdmin(admin.ModelAdmin):
    list_display = ("user", "plan_name", "budget_type", "budget_amount", "start_date", "end_date", "accept_sms", "created_at")
    list_filter = ("budget_type", "accept_sms", "created_at")
    search_fields = ("plan_name", "user__username")