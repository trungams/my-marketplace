from django.urls import path
from . import views

app_name = "marketplace"
urlpatterns = [
    path("", views.index, name="index"),
    path("api/products/view", views.retrieve_products, name="view_products"),
    path("api/products/<int:pk>/view", views.retrieve_single_product, name="view_single_product"),
    path("api/products/<int:pk>/add-to-cart", views.add_to_cart, name="add_to_cart"),
    path("api/cart/view", views.retrieve_cart, name="view_cart"),
]
