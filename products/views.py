from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
# a special object from Jango.db.models called Q to generate a more complex search query:
from django.db.models import Q
from django.db.models.functions import Lower
from .models import Product, Category

# define an all_products view which will render the products template
def all_products(request):
    """ A view to show all products, including sorting and search queries """

    # return all products from the database
    products = Product.objects.all()

    # ensure we don't get an error when loading the products page without a search term
    query = None

    # to capture a category parameter we'll start with it as none
    categories = None

    # to return the template properly when we're not using any sorting.
    sort = None
    direction = None

    # when a search query is submited it end up in the url as a GET parameter.
    # We can access those url parameter in the all_products view by checking whether request.get exists:
    if request.GET:
        # sort, direction and category parameters in the url, used in main-nav template
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            
            if sortkey == 'name':
                # in order to allow case-insensitive sorting on the name field
                # annotate all the products with a new field "lower_name"
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))

            # force categories to be sorted by name instead of their ids
            if sortkey == 'category':
                # double underscore syntax allows us to drill into a related model
                sortkey = 'category__name'

            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    # if the direction is descending reverse the order
                    sortkey = f'-{sortkey}'
            # use the order_by model method to actually sort the products 
            products = products.order_by(sortkey)


        # check whether category exists in requests.GET
        if 'category' in request.GET:
            # split category into a list
            categories = request.GET['category'].split(',')
            # filter the current query set of all products down to only products whose category name is in the list
            # look for the name field of the related category model using the double underscore syntax
            products = products.filter(category__name__in=categories)
            # filter all category objects down to the ones whose name is in the list from the URL
            # and get a list of actual category objects (so that we can access all their fields in the template)
            categories = Category.objects.filter(name__in=categories)

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

    current_sorting = f'{sort}_{direction}'
    
    # template variables to be returned from all_products view to the template:
    context = {
        # add all products to the context so products will be available in the template
        'products': products,

        # add the query to the context
        'search_term': query,

        # return the list of category objects to the context as a current_category
        'current_categories': categories,

        # return the current sorting methodology to the template
        'current_sorting': current_sorting,
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
