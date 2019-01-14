from django.urls import path
from . import views

app_name = "marketplace"
urlpatterns = [
    path("", views.index, name="index"),
    path("products/view", views.retrieve_products, name="view_products"),
    path("cart/view", views.retrieve_cart, name="view_cart"),
]
