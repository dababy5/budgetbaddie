from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.models import BudgetPlan
from accounts.views import get_purchase_info, sync_purchases


# Create your views here.
def index(request):
    return render(request, "index.html")

def signup(request):
    return render(request, "registration/signup.html")
    
def login(request):
    return render(request, "registration/login.html")

def connect(request):
    return render(request, "connect_bank.html")

@login_required
def user_home (request):
    user = request.user
    sync_purchases(user)
    plans = BudgetPlan.objects.filter(user=user).order_by("-created_at")  # newest first
    return render(request, "user/user_home.html", {"plans": plans})

def planner (request):
    return render(request, "user/budget_plan.html" )
def thanks (request):
    return render(request, "user/thanks.html")