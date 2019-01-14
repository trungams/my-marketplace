from django.shortcuts import render, redirect
from django.http import HttpResponseNotAllowed, JsonResponse
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required

from .models import *

# Create your views here.


def index(request):
    """TODO: return available URLs so that visitors know how to navigate

    :param request:
    :return:
    """
    return JsonResponse({"greeting": "Hello, world!"})


def retrieve_products(request):
    """TODO: write doc

    :param request:
    :return:
    """
    if request.method != "GET":
        return HttpResponseNotAllowed(request)
    else:
        ctx = {}

        product_name = request.GET.get("product", "")
        # price_range_lower = request.GET.get("lo", "0.00")
        # price_range_upper = request.GET.get("hi", "10000000000")
        category = request.GET.get("category", "")

        products_list = Product.objects.values(
            "title",
            "price",
            "inventory_count",
            "category",
            "description",
            "seller__username"
        ).filter(
            inventory_count__gt=0,
            title__icontains=product_name,
            category__icontains=category
        ).order_by("title")

        ctx["products"] = list(products_list)

        return JsonResponse(ctx)


@login_required()
def retrieve_cart(request):
    """TODO: write doc

    :param request:
    :return:
    """
    if request.method != "GET":
        return HttpResponseNotAllowed(request)
    else:
        ctx = {}

        current_cart, created = Cart.objects.get_or_create(user=request.user)

        cart_entries = CartEntry.objects.values(
            "product__title",
            "product_count",
            "cost"
        ).filter(
            associated_cart=current_cart
        )

        ctx["overview"] = current_cart.__str__()
        ctx["owner"] = current_cart.user.username
        ctx["items"] = current_cart.item_count
        ctx["total"] = current_cart.total_cost
        ctx["items list"] = list(cart_entries)

        return JsonResponse(ctx)


@login_required()
def add_to_cart(request):
    """TODO"""
    if request.method != "POST":
        return HttpResponseNotAllowed(request)
    else:
        pass


@login_required()
def checkout_cart(request):
    """TODO"""
    if request.method == "GET":
        pass
    elif request.method == "POST":
        pass
    else:
        return HttpResponseNotAllowed(request)


@login_required()
def update_inventory(request):
    """TODO"""
    if request.method == "GET":
        pass
    elif request.method == "POST":
        pass
    else:
        return HttpResponseNotAllowed(request)
