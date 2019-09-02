from django.contrib import admin
from django.urls import path
from .views import *

app_name = "campaign"

urlpatterns = [
    path('<slug:slug>', campProductList, name="campProList"),
]
