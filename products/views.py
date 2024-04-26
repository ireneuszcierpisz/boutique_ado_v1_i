from django.shortcuts import render
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
