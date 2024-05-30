from django.shortcuts import render, redirect, reverse
from django.contrib import messages

from .forms import OrderForm


def checkout(request):
    # get the bag from the session
    bag = request.session.get('bag', {})
    if not bag:
        # if there's nothing in the bag add an error message
        messages.error(request, "There's nothing in your bag at the moment")
        # and redirect back to the products page
        # this will prevent people from manually accessing the URL by typing /checkout
        return redirect(reverse('products'))

    # create an empty instance of OrderForm class
    order_form = OrderForm()
    # create a checkout template
    template = 'checkout/checkout.html'
    # create a context containing the order form
    context = {
        'order_form': order_form,
        # copy the public key from https://dashboard.stripe.com/test/apikeys
        'stripe_public_key': 'pk_test_51PLiQwKdU2DfvUQTqrtNHDRZCsckN6c3uFqJ47ugaYWliYUNloH3ji6JfBJv6vhaFh5gvYMd4fC51vNzGwkn66K90098t6jPpd',
        'client_secret': 'test client secret',
    }

    return render(request, template, context)