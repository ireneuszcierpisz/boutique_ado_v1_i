from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404

# import messages and keep users informed of everything that's going on across the entire site
# by sending messages through the Django messages framework
from django.contrib import messages

from products.models import Product

# define a view which will render the bag template
def view_bag(request):
    """
    A view to return the bag contents page
    """
    return render(request, 'bag/bag.html')


# We'll submit the form product_detail.html to this view including the product id and the quantity
def add_to_bag(request, item_id):
    """ Add a quantity of the specified product to the shopping bag """

    # to make messages works we need
    # product = Product.objects.get(pk=item_id)
    # use get_object_or_404 just in case the product isn't found
    product = get_object_or_404(Product, pk=item_id)

    # get the quantity from the form
    # convert it to an integer since it'll come from the template as a string
    quantity = int(request.POST.get('quantity'))

    # get the redirect URL from the form, so we know where to redirect once the process here is finished
    redirect_url = request.POST.get('redirect_url')

    # initial value of a product size
    size = None
    # if 'product_size' name of selector from product_detail template form
    if 'product_size' in request.POST:
        size = request.POST['product_size']


    # HTTP every request-response cycle between the server and the client, 
    # in our case between the django view on the server-side and our form making the request on the client-side,
    # uses what's called a session, to allow information to be stored until the client and server are done communicating.
    # It allows to store the contents of the shopping bag in the HTTP session, while the user browses the site 
    # and adds items to be purchased, by storing the shopping bag in the session. It will persist until the user closes their browser.
    # A session variable bag accesses the requests session and first check if there's a 'bag' key in the session dictionary
    # and if not we'll create an empty dictionary
    bag = request.session.get('bag', {})

    # check if a product with sizes is being added to the bag
    if size:
        if item_id in list(bag.keys()):
            if size in bag[item_id]['items_by_size'].keys():
                bag[item_id]['items_by_size'][size] += quantity
                messages.success(request, f'Updated size {size.upper()} {product.name} quantity to {bag[item_id]["items_by_size"][size]}')
            else:
                bag[item_id]['items_by_size'][size] = quantity
                messages.success(request, f'Added size {size.upper()} {product.name} to your bag')
        # If the item's not already in the bag we need to add it as a dictionary with a key of 'items_by_size'
        # since we may have multiple items with this item_id but different sizes.        
        else:
            bag[item_id] = {'items_by_size': {size: quantity}}
            messages.success(request, f'Added size {size.upper()} {product.name} to your bag')
    else:
        # add the item to the bag
        # if there's already a key in the bag dictionary matching product id, increment its quantity
        if item_id in list(bag.keys()):
            bag[item_id] += quantity
            messages.success(request, f'Updated {product.name} quantity to {bag[item_id]}')
        else:
            # create a key of the items id and set it equal to the quantity
            bag[item_id] = quantity
            # ref to the toast; add a message to the request object and use string formatting 
            # to let the user know they've added a product to their bag
            messages.success(request, f'Added {product.name} to your bag')

    # put the bag variable into the session which itself is a python dictionary
    request.session['bag'] = bag

    # ! Because bag is a session variable we can access it anywhere we can access the request object
    # like in our views or the custom context processor we made in context.py

    # # print the shopping bag from the session to the console
    # print(request.session['bag'])

    # redirect the user back to the redirect_url
    return redirect(redirect_url)


# Write the views to handle updating product quantities
# take the request and item id as parameters
def adjust_bag(request, item_id):
    """Adjust the quantity of the specified product to the specified amount"""

    product = get_object_or_404(Product, pk=item_id)

    # coming from a form on the shopping bag page which will contain the new quantity the user wants in the bag
    quantity = int(request.POST.get('quantity'))
    size = None

    if 'product_size' in request.POST:
        size = request.POST['product_size']

    bag = request.session.get('bag', {})

    # If there's a size find that specific size and either set its quantity to the updated one
    if size:
        if quantity > 0:
            bag[item_id]['items_by_size'][size] = quantity
            messages.success(request, f'Updated size {size.upper()} {product.name} quantity to {bag[item_id]["items_by_size"][size]}')
        
        else:
            # remove the size if the quantity submitted is zero
            del bag[item_id]['items_by_size'][size]
            # remove the item entirely if there is no size
            if not bag[item_id]['items_by_size']:
                bag.pop(item_id)
            messages.success(request, f'Removed size {size.upper()} {product.name} from your bag')
    else:
        # if quantity is greater than zero set the items quantity accordingly
        if quantity > 0:
            bag[item_id] = quantity
            messages.success(request, f'Updated {product.name} quantity to {bag[item_id]}')
        # otherwise remove the item
        else:
            bag.pop(item_id)
            messages.success(request, f'Removed {product.name} from your bag')

    request.session['bag'] = bag

    # use the reverse function to redirect back to the view_bag URL 
    return redirect(reverse('view_bag'))


# Write the view to handle removing product from the bag entirely
def remove_from_bag(request, item_id):
    """Remove the item from the shopping bag"""

    # wrap the block of code in a try block to catch any exceptions that happen in order to return a 500 server error
    try:
        product = get_object_or_404(Product, pk=item_id)
        size = None
        if 'product_size' in request.POST:
            size = request.POST['product_size']
        bag = request.session.get('bag', {})

        if size:
            # We want to remove only the specific size the user requested
            # delete that size key in the items_by_size dictionary
            del bag[item_id]['items_by_size'][size]
            if not bag[item_id]['items_by_size']:
                bag.pop(item_id)
            messages.success(request, f'Removed size {size.upper()} {product.name} from your bag')
        else:
            # remove the item popping it out of the bag
            bag.pop(item_id)
            messages.success(request, f'Removed {product.name} from your bag')

        request.session['bag'] = bag

        # Because this view will be posted to from a JavaScript function 
        # instead of returning a redirect return an actual 200 HTTP response implying that the item was successfully removed
        return HttpResponse(status=200)

    # if any exception return a 500 server error
    except Exception as e:
        # if any error occurs in the removal process the user will get a notification about it 
        messages.error(request, f'Error removing item: {e}')
        return HttpResponse(status=500)