"""
URL configuration for budgetbaddie project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from routing.views import signup, login, index, user_home,connect,planner,thanks
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import login_view, signup_view,connect_bank,test_sms, gemini_process_purchases,create_budget_plan

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include ("accounts.urls")),
    path("", TemplateView.as_view(template_name="index.html"), name="index"),
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("user_home/", user_home, name="user_home"),
    path("user_home/gemini", gemini_process_purchases, name="gemini_process_purchases"),
    path("connect_bank/", connect_bank, name="connect_bank"),
    path("test-sms/", test_sms, name="test_sms"),
    path("budget_plan/",create_budget_plan,name="budget_plan"),
    path("thanks/",thanks,name="thanks")
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)