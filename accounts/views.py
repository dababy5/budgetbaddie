# Create your views here.
from django.shortcuts import render, redirect

from django.contrib.auth.models import User
from .forms import SignUpForm, LoginForm,BankForm
from .models import Profile

from django.contrib.auth import authenticate, login



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
    
        
                return redirect("user_home")
    
    return render(request,"registration/connect_bank.html")


