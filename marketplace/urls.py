from django.urls import path
from . import views

app_name = "marketplace"
urlpatterns = [
    path("", views.index, name="index"),
    path("api/products/view", views.api_retrieve_products, name="api_view_products"),
    path("api/products/<int:pk>/view", views.api_retrieve_single_product, name="api_view_single_product"),
    path("api/products/<int:pk>/add-to-cart", views.api_add_to_cart, name="api_add_to_cart"),
    path("api/cart/view", views.api_retrieve_cart, name="api_view_cart"),
]
