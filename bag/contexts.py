# use the decimal function since this is a financial transaction and using float is susceptible to rounding errors.
# in general using decimal is preferred when working with money because it's more accurate.
from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product

# The context processor as bag_contents(request) function
"""
In order to make this context processor available to the entire application
we need to add it to the list of context_processors in the TEMPLATES variable in settings.py
This context concept is the same as the context we use in our views 
but the difference is that we're returning the context directly 
and making it available to all templates by putting it in settings.py
"""
# we'll access the shopping bag stored in the session within the context processor in order 
# to add all the bag's current items to the context of all templates

# take the request as a parameter
def bag_contents(request):
    # create an empty list for the bag items to live in
    bag_items = []
    total = 0
    product_count = 0

    # Access the shopping bag in the session
    bag = request.session.get("bag", {})

    # add the products and their data to the bag items list
    for item_id, quantity in bag.items():
        # get the product
        product = get_object_or_404(Product, pk=item_id)
        # add product quantity times the price to the total
        total += quantity * product.price
        # increment the product count by the quantity
        product_count += quantity
        # add to the list of bag items a dictionary also containing the product object itself
        # that will give us access to all the other product fields such as the product image 
        # when iterating through the bag items in our templates
        bag_items.append({
            'item_id': item_id,
            'quantity': quantity,
            'product': product,
        })

    if total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        # For convenience let the user know how much more they need to spend to get free delivery:
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        delivery = 0
        free_delivery_delta = 0
    
    grand_total = delivery + total
    
    context = {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'grand_total': grand_total,
    }

    # returns a dictionary available to all templates across the entire application
    # much like we can use request.user in any template due to the presence of the built-in request context processor
    return context