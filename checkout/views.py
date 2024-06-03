from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm

# import the bag_contents() as a function to calculate the current bag total in the view
# what is needed to call the confirmCardPayment method from stripe js
from bag.contexts import bag_contents

import stripe

""" Stripe works with what are called payment intents.
The process: when a user hits the checkout page
the checkout view will call out to stripe and create a payment intent
for the current amount of the shopping bag.
When stripe creates the intent it'll also have a secret that identifies it 
and this secret will be returned to us and we'll send it to the template as the client secret variable. """

def checkout(request):
    # create the payment intent
    
    # set variables for the public and secret keys
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    
    # get the bag from the session
    bag = request.session.get('bag', {})
    if not bag:
        # if there's nothing in the bag add an error message
        messages.error(request, "There's nothing in your bag at the moment")
        # and redirect back to the products page
        # this will prevent people from manually accessing the URL by typing /checkout
        return redirect(reverse('products'))

    # get Python dictionary as current_bag than not to overwrite the bag variable that already exists
    current_bag = bag_contents(request)
    total = current_bag['grand_total']
    # set stripe_total multiplying total by a hundred and round it to zero decimal places using the round function 
    # because stripe require the amount to charge as an integer
    stripe_total = round(total * 100)

    # set the secret key on stripe
    stripe.api_key = stripe_secret_key
    # create the payment intent giving it the amount and the currency:
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
    )

    # print to the terminal the payment intent which is back from stripe like a dictionary with many keys
    print(intent)

    # create an empty instance of OrderForm class
    order_form = OrderForm()

    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. \
            Did you forget to set it in your environment?')

    # create a checkout template
    template = 'checkout/checkout.html'
    # create a context containing the order form
    context = {
        'order_form': order_form,
        # copy the public key from https://dashboard.stripe.com/test/apikeys and put it to the gitpod Environment Variables as STRIPE_PUBLIC_KEY
        'stripe_public_key': stripe_public_key,
        # we'll send a secret created by Stripe to the checkout template as the client_secret variable
        'client_secret': intent.client_secret,
    }

    return render(request, template, context)