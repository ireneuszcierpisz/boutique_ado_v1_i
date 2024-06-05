from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product
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

    """
    When a user submits their payment information we also create the order in the database
    and redirect them to a success page.
    """
    # first check whether the method is POST
    if request.method == 'POST':
        # get a shopping bag
        bag = request.session.get('bag', {})

        # put the form data into a dictionary; fields can come directly from the form.
        # we skip the save infobox which doesn't have a field on the order model.
        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }
        # create an instance of the form using the form data
        order_form = OrderForm(form_data)

        # If the form is valid save the order
        if order_form.is_valid():
            order = order_form.save()
            # then iterate through the bag items to create each line item;code like that in the context processor 
            for item_id, item_data in bag.items():
                try:
                    # get the product ID out of the bag
                    product = Product.objects.get(id=item_id)
                    # if its value is an integer we know we're working with an item that doesn't have sizes
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            # as an item that doesn't have sizes the quantity is just the item_data
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        # if the item has sizes iterate through each size and create a line item accordingly
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
                # if a product isn't found
                except Product.DoesNotExist:
                    messages.error(request, (
                        "One of the products in your bag wasn't found in our database. "
                        "Please call us for assistance!")
                    )
                    # delete the empty order
                    order.delete()
                    # return the user to the shopping bag page
                    return redirect(reverse('view_bag'))

            # whether or not the user wanted to save their profile information to the session
            request.session['save_info'] = 'save-info' in request.POST
            return redirect(reverse('checkout_success', args=[order.order_number]))
        else:
            messages.error(request, 'There was an error with your form. \
                Please double check your information.')

    # else handle the GET requests
    else:
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


# take the order number and render a success page letting the user know that their payment is complete.
def checkout_success(request, order_number):
    """
    Handle successful checkouts
    """
    # check whether the user wanted to save their information by getting that from the session
    save_info = request.session.get('save_info')
    # get the order created in the previous view
    order = get_object_or_404(Order, order_number=order_number)
    # attach a success message letting the user know what their order number is
    # and that will be sending an email to the email they put in the form.
    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.')
    # delete the user shopping bag from the session since it'll no longer be needed for this session
    if 'bag' in request.session:
        del request.session['bag']

    # Set the template and the context
    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }
    # render checkout_success template
    # send the order back to the template
    return render(request, template, context)    