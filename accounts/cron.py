from .models import BudgetPlan
from .views import check_budget_and_alert

def run_budget_checks():
    for plan in BudgetPlan.objects.all():
        user = plan.user
        check_budget_and_alert(user, plan)
