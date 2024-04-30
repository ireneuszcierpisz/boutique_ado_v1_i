from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
# a special object from Jango.db.models called Q to generate a more complex search query:
from django.db.models import Q
from .models import Product

# define an all_products view which will render the products template
def all_products(request):
    """ A view to show all products, including sorting and search queries """

    # return all products from the database
    products = Product.objects.all()

    # ensure we don't get an error when loading the products page without a search term
    query = None

    # when a search query is submited it end up in the url as a GET parameter.
    # We can access those url parameter in the all_products view by checking whether request.get exists:
    if request.GET:
        # Since we named the text input in the form in base.html 'q', we can check if 'q' is in request.GET
        if 'q' in request.GET:
            query = request.GET['q']
            #If the query is blank it's not going to return any results 
            if not query:
                # we use the Django messages framework to attach an error message to the request
                messages.error(request, "You didn't enter any search criteria")
                # and redirect back to the products url
                return redirect(reverse('products'))
            # construct queries:
            # set a variable named queries equal to a Q object,where the name contains the query or the description contains the query
            # case-insensitive containment test uses icontains statement
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            # pass queries to the filter method in order to actually filter the products
            products = products.filter(queries)

    # add all products to the context so products will be available in the template
    context = {
        'products': products,
        # add the query to the context
        'search_term': query,
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
