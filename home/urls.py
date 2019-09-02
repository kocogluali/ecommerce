from django.urls import path
from .views import filterSearchProduct

app_name = "home"

urlpatterns = [
    # AJAX REQUEST
    path('filterSearchProduct/', filterSearchProduct, name="filterSearchProduct"),  # filter search product search.html
    # END AJAX REQUEST
]
