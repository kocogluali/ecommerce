from django.urls import path
from .views import *

app_name = "blog"

urlpatterns = [
    path('',blogList,name="blogListAll"),
    path('<slug:category>/',blogList,name="blogList"),
    path('<slug:category>/<slug:post>/',blogDetail,name="blogDetail"),
]
