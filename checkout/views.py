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
    }

    return render(request, template, context)