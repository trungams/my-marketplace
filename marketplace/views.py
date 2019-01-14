from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseNotAllowed, JsonResponse
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required

from .models import *
from .forms import *

# Create your views here.


def index(request):
    """TODO: return available URLs so that visitors know how to navigate

    :param request:
    :return:
    """
    return render(request, "marketplace/index.html")


def register(request):
    """TODO"""
    if request.user.is_authenticated:
        return redirect("index")
    if request.method == "GET":
        form = CustomUserCreationForm()
        return render(request, "registration/register.html", {"form": form})
    elif request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
        return redirect("register")
    else:
        return HttpResponseNotAllowed(request)


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


def retrieve_single_product(request, pk):
    """TODO"""
    if request.method != "GET":
        return HttpResponseNotAllowed(request)
    else:
        ctx = {}

        current_product = get_object_or_404(Product, pk=pk)

        ctx["product name"] = current_product.title
        ctx["price"] = current_product.price
        ctx["availability"] = current_product.inventory_count
        ctx["category"] = current_product.category
        ctx["description"] = current_product.description
        ctx["seller"] = current_product.seller.username

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
def add_to_cart(request, pk):
    """TODO"""
    current_product = get_object_or_404(Product, pk=pk)

    if request.method == "GET":
        ctx = {}

        form = CartEntryAddForm()

        ctx["form"] = form
        ctx["product"] = current_product.title
        ctx["available"] = current_product.inventory_count
        ctx["price"] = current_product.price
        return render(request, "marketplace/add-to-cart.html", ctx)
    elif request.method == "POST":
        ctx = {}

        current_cart, created = Cart.objects.get_or_create(user=request.user)

        form = CartEntryAddForm(request.POST)

        try:
            if form.is_valid():
                # process data in form.cleaned_data as required
                if current_product.inventory_count < form.cleaned_data["product_count"]:
                    ctx["success"] = False
                    ctx["message"] = "Cannot add more than the current number of available items."
                else:
                    new_cart_entry = form.save(commit=False)

                    # adding necessary information before adding to database
                    new_cart_entry.associated_cart = current_cart
                    new_cart_entry.product = current_product
                    new_cart_entry.save()

                    ctx["success"] = True
            else:
                ctx["success"] = False
                ctx["message"] = "Invalid form data!"
        except ValidationError:
            ctx["success"] = False
            ctx["message"] = "Invalid form data!"

        return JsonResponse(ctx)
    else:
        return HttpResponseNotAllowed(request)


@login_required()
def checkout_cart(request):
    """TODO"""
    if request.method == "GET":
        # TODO: render a template with form to checkout
        return HttpResponseNotAllowed(request)
    elif request.method == "POST":
        pass
    else:
        return HttpResponseNotAllowed(request)


@login_required()
def update_inventory(request):
    """TODO"""
    if request.method == "GET":
        # TODO: render a template with form to modify inventory
        return HttpResponseNotAllowed(request)
    elif request.method == "POST":
        pass
    else:
        return HttpResponseNotAllowed(request)
