# Create your views here.
from django.shortcuts import render, redirect

from django.contrib.auth.models import User
from .forms import SignUpForm, LoginForm, BankForm, ChatBotInput
from .models import Profile, ItemPurchaseHistory
from decouple import config
import google as genai
from django.contrib.auth import authenticate, login
import requests
from django.http import HttpResponse
from .utils import send_sms_via_email


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
            return redirect("user_home")
    
    return render(request,"registration/connect_bank.html")

def get_purchase_info(request):
    if request.method == "GET":
        capital_one_api_key = config("CAPITAL_API")
        user = request.user
        account_id = user.profile.account_id
        
        api_url = f"http://api.reimaginebanking.com/accounts/{account_id}/purchases?key={capital_one_api_key}"

        response = requests.get(api_url)

        data = response.json()
        purchase_data = []

        for item in data:
            purchase_type = item.get("type", "No type available")
            merchant_id = item.get("merchant_id", "No merchant ID available")
            purchase_date = item.get("purchase_date", "No purchase data available")
            amount = item.get("amount", "No amount available")
            description = item.get("description", "No description available")

            ItemPurchaseHistory.objects.create(user=user, purchase_type=purchase_type, merchant_id=merchant_id, purchase_date=purchase_date, amount=amount, description=description)
            ItemPurchaseHistory.save()

            purchase_data.append({
                "type": purchase_type,
                "merchant_id": merchant_id,
                "purchase_date": purchase_date,
                "amount": amount,
                "description": description
            })
            
            # change the endpoints of these renderings, these are just placements
            return render(request, "user/user_home.html", {"purchase_data": purchase_data})
    return render(request, "user/user_home.html")

def gemini_process_purchases(request):
    if request.method == "POST":
        form = ChatBotInput(request.POST)
        if form.is_valid():

            message = form.cleaned_data["message"]

            gemini_api_key = config("GEMINI_API")
            client = genai.Client(api_key=gemini_api_key)

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=message
            )

            return render(request, "user/user_home.html", {"form": form, "response": response})
    else:
        # to handle initial get request
        form = ChatBotInput()

    return render(request, "user/user_home.html", {"form": form})
            
def test_sms(request):
    profile = request.user.profile.phone_number
    result = send_sms_via_email(f"{profile}", "vtext.com", "Hello")
    return HttpResponse(result)


def check_budget_and_alert(user):
    # Example: sum all transactions for this user
    total = user.transactions.aggregate(Sum("amount"))["amount__sum"] or 0
    WEEKLY_BUDGET_LIMIT = 200

    if total >= WEEKLY_BUDGET_LIMIT:
        send_sms_via_email(
            phone_number="5551234567",       # your number
            carrier_domain="vtext.com",      # your carrier domain
            message=f"🚨 Alert! You’ve hit your budget limit: ${total}"
        )