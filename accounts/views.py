# Create your views here.
from django.shortcuts import render, redirect

from django.contrib.auth.models import User
from .forms import SignUpForm, LoginForm, BankForm, ChatBotInput
from .models import Profile, ItemPurchaseHistory,BudgetPlan
from decouple import config
from google import genai
from django.contrib.auth import authenticate, login
import requests
from django.http import HttpResponse
from .utils import send_sms_via_email
from datetime import datetime,date
from decimal import Decimal
from django.db.models import Sum
from datetime import date, timedelta
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils.dateparse import parse_date

# LOGIN/SIGN UP
def signup_view(request):

    if request.method == "POST":
        form = SignUpForm(request.POST)

        if form.is_valid():

            phone_number = form.cleaned_data["phone_number"]
            # creates instance of User class and creates an individual user
            user = form.save()

            Profile.objects.create(user=user, phone_number=phone_number)

            login(request, user)
            return redirect("connect_bank")
        
    else:
        form = SignUpForm()

    return render(request, "registration/signup.html", {"form": form})



def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("user_home")
            
    else:
        form = LoginForm()
    
    return render(request, "registration/login.html", {"form": form})

def connect_bank(request):
    if request.method == "POST":

        form = BankForm(request.POST)
        if form.is_valid():
            bank_name = form.cleaned_data["bank_name"]
            bank_accountId = form.cleaned_data["bank_accountID"]
            bank_customerId = form.cleaned_data["bank_customerId"]
    
            profile = request.user.profile

            profile.bank_accountId = bank_accountId
            profile.bank_customerId = bank_customerId
            profile.save()

            get_purchase_info(request)
            return redirect("user_home")
    
    return render(request,"registration/connect_bank.html")


def sync_purchases(user):
    capital_one_api_key = config("CAPITAL_API")
    account_id = user.profile.bank_accountId
    api_url = f"http://api.nessieisreal.com/accounts/{account_id}/purchases?key={capital_one_api_key}"

    response = requests.get(api_url)
    data = response.json()

    for item in data:
        raw_date = item.get("purchase_date")
        if raw_date:
            try:
                purchase_date = date.fromisoformat(raw_date)
            except ValueError:
                pass

        ItemPurchaseHistory.objects.get_or_create(
            user=user,
            merchant_id=item.get("merchant_id", "N/A"),
            purchase_date=purchase_date,
            defaults={
                "purchase_type": item.get("type", "N/A"),
                "amount": Decimal(item.get("amount", 0)),
                "description": item.get("description", "No description"),
            },
        )

# keep your view for manual sync
def get_purchase_info(request):
    sync_purchases(request.user)
    return redirect("user_home")



def gemini_process_purchases(request):
   if request.method == "POST":
        form = ChatBotInput(request.POST)
        if form.is_valid():
            message = form.cleaned_data["message"]

            user_purchases = ItemPurchaseHistory.objects.filter(user=request.user)

            purchase_context = "Here is the user's purchase history:\n"
            for item in user_purchases:
                purchase_context += f"- Date: {item.purchase_date}, Amount: ${item.amount}, Description: {item.description}\n"
            full_prompt = f"{purchase_context}\n\nBased on that history, please answer the following question:\n{message}"

            try:
                # MIGHT NEED TO HARCODE THIS. I HAD TROUBLE IMMPORTING THE .ENV FILE
                api_key=config('GEMINI_API')
                client = genai.Client(api_key=api_key)

                response = client.models.generate_content(
                    model="gemini-2.5-flash", 
                    contents=full_prompt
                )
                print(response)

                api_response_text = response.text 

            except Exception as e:
                api_response_text = f"Sorry, there was an error with the API: {e}"

            return render(request, "partials/chat_message.html", {"response": api_response_text})
            
def test_sms(request):
    from decouple import config
    from google import genai
    from .models import ItemPurchaseHistory

    phone_number = request.user.profile.phone_number

    # Build purchase history context
    user_purchases = ItemPurchaseHistory.objects.filter(user=request.user)
    purchase_context = "Here is the user's purchase history:\n"
    for item in user_purchases:
        purchase_context += f"- Date: {item.purchase_date}, Amount: ${item.amount}, Description: {item.description}\n"

    # Prompt Gemini to generate a short SMS
    full_prompt = (
        f"{purchase_context}\n\n"
        "Write a short, friendly SMS alert (max 160 characters) reminding the user about their most recent spending. so they can be better"
    )

    try:
        api_key = config("GEMINI_API")
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt
        )
        ai_message = response.text
    except Exception as e:
        ai_message = f"Error with Gemini: {e}"

    # Send the AI-generated SMS
    result = send_sms_via_email(
        phone_number=phone_number,
        carrier_domain="vtext.com",
        message=ai_message
    )

    return HttpResponse(result)


def create_budget_plan(request):
    if request.method == "POST":
        plan_name = request.POST.get("plan_name")
        budget_type = request.POST.get("budget_type") or 0           # weekly|monthly|yearly|custom
        budget_amount = Decimal(request.POST.get("budget_amount"))
        start_date_str = request.POST.get("start_date") or None
        end_date_str = request.POST.get("end_date") or None
        accept_sms = request.POST.get("accept_sms") == "on"

        # create the plan
        plan = BudgetPlan.objects.create(
            user=request.user,
            plan_name=plan_name,
            budget_type=budget_type,
            budget_amount=budget_amount,
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date() if start_date_str else None,
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else None,
            accept_sms=accept_sms,
        )

        # (Optional) run a first check right after saving
        check_budget_and_alert(request.user, plan)

        return redirect("thanks")

    return render(request, "user/budget_plan.html")


def check_budget_and_alert(user, plan: BudgetPlan):
    today = date.today()

    # 1) determine start/end based on plan type
    if plan.budget_type == "weekly":
        start = today - timedelta(days=today.weekday())  # Monday
        end = start + timedelta(days=6)
    elif plan.budget_type == "monthly":
        start = today.replace(day=1)
        end = _month_end(today)
    elif plan.budget_type == "yearly":
        start = date(today.year, 1, 1)
        end = date(today.year, 12, 31)
    elif plan.budget_type == "custom":
        start = plan.start_date
        end = plan.end_date
    else:
        return  # unknown type, bail

    # guard if custom dates missing
    if start is None or end is None:
        return

    # 2) sum purchases in range (after your sync runs elsewhere)
    total = (
        ItemPurchaseHistory.objects
        .filter(user=user, purchase_date__range=(start, end))
        .aggregate(Sum("amount"))["amount__sum"]
        or Decimal("0")
    )

    # 3) compare and alert
    if total >= plan.budget_amount and plan.accept_sms:
        carrier = "vtext.com"  # consider storing on Profile
        send_sms_via_email(
            phone_number=user.profile.phone_number,
            carrier_domain=carrier,
            message=(
                f"🚨 {plan.plan_name}: spent ${total} of ${plan.budget_amount} "
                f"({plan.budget_type})"
            ),
        )

def _month_end(d: date) -> date:
    if d.month == 12:
        return date(d.year, 12, 31)
    first_next = d.replace(day=1, month=d.month + 1)
    return first_next - timedelta(days=1)

def delete_budget_plan(request, plan_id):
    if request.method == "POST":
        plan = get_object_or_404(BudgetPlan, id=plan_id, user=request.user)
        plan.delete()
        return HttpResponse(status=204)


def spending_chart_data(request):
    user = request.user

    start_param = request.GET.get("start")
    end_param = request.GET.get("end")

    start = parse_date(start_param) if start_param else None
    end = parse_date(end_param) if end_param else None

    qs = ItemPurchaseHistory.objects.filter(user=user)

    if start and end:
        qs = qs.filter(purchase_date__range=[start, end])

    purchases = qs.order_by("purchase_date")

    labels = [p.purchase_date.strftime("%Y-%m-%d") for p in purchases]
    data = [float(p.amount) for p in purchases]

    return JsonResponse({
        "labels": labels,
        "data": data,
    })
