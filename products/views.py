from django.shortcuts import render, get_object_or_404
from .models import Product

# Create your views here.
# define an all_products view which will render the products template
def all_products(request):
    """ A view to show all products, including sorting and search queries """

    # return all products from the database
    products = Product.objects.all()

    # add all products to the context so products will be available in the template
    context = {
        'products': products,
    }

    return render(request, 'products/products.html', context)

# the view which take an individual product_id as a parameter and returns the template including the product
def product_detail(request, product_id):
    """ A view to show individual product details """

    # return only one product from the database
    product = get_object_or_404(Product, pk=product_id)

    # add product to the context so 'product' will be available in the template
    context = {
        'product': product,
    }

    return render(request, 'products/product_detail.html', context)
