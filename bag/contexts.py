# use the decimal function since this is a financial transaction and using float is susceptible to rounding errors.
# in general using decimal is preferred when working with money because it's more accurate.
from decimal import Decimal
from django.conf import settings

# The context processor  bag_contents(request)
"""
In order to make this context processor available to the entire application
we need to add it to the list of context_processors in the TEMPLATES variable in settings.py
This context concept is the same as the context we use in our views 
but the difference is that we're returning the context directly 
and making it available to all templates by putting it in settings.py.
"""

# take the request as a parameter
def bag_contents(request):
    # create an empty list for the bag items to live in
    bag_items = []
    total = 0
    product_count = 0

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