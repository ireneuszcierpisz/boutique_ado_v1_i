"""
If the users intentionally or accidentally closes the browser window after the payment is confirmed 
but before the form is submitted we would end up with a payment in stripe but no order in our database. 
What's more, if we were building a real store that needed to complete post order operations like sending internal 
email notifications, none of that stuff would be triggered because the user never fully completed their order.
This could result in a customer being charged and never receiving a confirmation email or even worse never receiving
what they ordered.
We have to prevent this situation. Each time an event occurs on stripe such as a payment intent being created,
a payment being completed and so on stripe sends out what's called a webhook we can listen for.
Webhooks are like the signals django sends each time a model is saved or deleted except that they're sent securely
from stripe to a URL we specify.
		To handle these webhooks create custom class called StripeWH_Handler.
        Further by using a class we can make our work reusable such that we could import it into other projects.
"""        
# to get this thing listening we need create a url for it in checkout/urls.py

from django.http import HttpResponse

from .models import Order, OrderLineItem
from products.models import Product

import json
import time


class StripeWH_Handler:
    """Handle Stripe webhooks"""

    # use the __init__ method of the class, which is a setup method that's called every time an instance of the class
    # is created, to assign the request as an attribute of the class 
    # just in case we need to access any attributes of the request coming from stripe
    def __init__(self, request):
        self.request = request

    # for each type of webhook we want a different method to handle it which makes them easy to manage 
    # and makes it easy to add more as stripe adds new ones

    # take the event stripe is sending us
    # the generic handle event method here is receiving the webhook we are otherwise not handling
    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        # return an HTTP response indicating the event was received
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe.
        This webhook will be sent each time a user completes the payment process.
        """
        print()
        print(' !! going to get an intent from stripe !! ')
        print()

        # get the payment intent which has all our customer's information
        intent = event.data.object
        # print out the payment intent coming from stripe once the user makes a payment; 
        # it have a metadata attached
        print(intent)

        # use the payment intent to create an order in case the form isn't submitted for some reason 
        # like if the user closes the page on the loading screen
        # get the payment intent id
        pid = intent.id
        # get shopping bag and the user's save info preference from the metadata added in cache_checkout_data view
        bag = intent.metadata.bag
        save_info = intent.metadata.save_info

        #billing_details = intent.charges.data[0].billing_details
        billing_details = stripe_charge.billing_details # updated
        shipping_details = intent.shipping
        #grand_total = round(intent.charges.data[0].amount / 100, 2)
        grand_total = round(stripe_charge.amount / 100, 2) # updated

        """ Clean data in the shipping details """
        # to ensure the data is in the same form as what we want in the database
        # replace any empty strings in the shipping details with None 
        # since stripe store them as blank strings which is not the same as the null value 
        # we want in the database.
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        """ Most of the time when a user checks out, everything go well and the form
            is submitted so the order should already be in our database when we receive this webhook.
            The first thing then is to check if the order exists already. """
        # assume the order doesn't exist
        order_exists = False

        # In case if the view is slow for some reason and hasn't created the order by the time we get the webhook from stripe
        # instead of immediately creating the order if it's not found in the database let's introduce a bit of delay 
        # create a variable attempt and set it to 1
        attempt = 1
        # create a while loop that will execute up to 5 times.
        while attempt <= 5:
            # try to get the order using all the information from the payment intent
            try:
                order = Order.objects.get(
                    # use the __iexact lookup field to make it an exact match but case-insensitive
                    full_name__iexact=shipping_details.name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=shipping_details.phone,
                    country__iexact=shipping_details.address.country,
                    postcode__iexact=shipping_details.address.postal_code,
                    town_or_city__iexact=shipping_details.address.city,
                    street_address1__iexact=shipping_details.address.line1,
                    street_address2__iexact=shipping_details.address.line2,
                    county__iexact=shipping_details.address.state,
                    grand_total=grand_total,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                order_exists = True
                break
            # now instead of creating the order if the order is not found the first time increment attempt by 1
            # and then use python's time module to sleep for one second, this means that
            # the webhook handler will try to find the order five times over five seconds 
            # before giving up and creating the order itself
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)
        # If an order does exists we'll just return a response, and say everything is all set
        if order_exists:
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
                status=200)
        # if an order doesn't exists we'll create it here in the webhook
        else:
            order = None
            try:
                # create order with Order.objects.create using all the data from the payment intent
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.address.country,
                    postcode=shipping_details.address.postal_code,
                    town_or_city=shipping_details.address.city,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    county=shipping_details.address.state,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                # load the bag from the JSON version in the payment intent instead of from the session
                for item_id, item_data in json.loads(bag).items():
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
            except Exception as e:
                # if anything goes wrong delete the order if it was created.
                if order:
                    order.delete()
                # and return a 500 server error response to stripe,
                # which cause stripe to automatically try the webhook again later.
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500)
        # the order have been created by the webhook handler so we should return a response to stripe indicating that
        return HttpResponse(
            content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook',
            status=200)
    """ 
    If our view is slow for some reason and hasn't created the order by the time we get the webhook from stripe,
    means that the view will create the order but it might be a few seconds late.
    This is not good because our webhook handler won't find the order when it first gets the webhook from stripe
    and will create the order itself resulting in the same order being added to the database twice, 
    once the view finally finishes.
    This is, one of the downfalls of asynchronous applications where multiple processes are happening at once.
    So, instead of just immediately going to create the order if it's not found in the database we introduce 
    a delay using a variable called attempt. 
    """


    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Payment Failed Webhook received: {event["type"]}',
            status=200)




# from django.http import HttpResponse

# from .models import Order, OrderLineItem
# from products.models import Product

# import json
# import time

# class StripeWH_Handler:
#     """Handle Stripe webhooks"""

#     def __init__(self, request):
#         self.request = request

#     def handle_event(self, event):
#         """
#         Handle a generic/unknown/unexpected webhook event
#         """
#         return HttpResponse(
#             content=f'Unhandled webhook received: {event["type"]}',
#             status=200)

#     def handle_payment_intent_succeeded(self, event):
#         """
#         Handle the payment_intent.succeeded webhook from Stripe
#         """
#         intent = event.data.object
#         pid = intent.id
#         bag = intent.metadata.bag
#         save_info = intent.metadata.save_info

#         billing_details = intent.charges.data[0].billing_details
#         shipping_details = intent.shipping
#         grand_total = round(intent.charges.data[0].amount / 100, 2)

#         # Clean data in the shipping details
#         for field, value in shipping_details.address.items():
#             if value == "":
#                 shipping_details.address[field] = None

#         order_exists = False
#         attempt = 1
#         while attempt <= 5:
#             try:
#                 order = Order.objects.get(
#                     full_name__iexact=shipping_details.name,
#                     email__iexact=billing_details.email,
#                     phone_number__iexact=shipping_details.phone,
#                     country__iexact=shipping_details.address.country,
#                     postcode__iexact=shipping_details.address.postal_code,
#                     town_or_city__iexact=shipping_details.address.city,
#                     street_address1__iexact=shipping_details.address.line1,
#                     street_address2__iexact=shipping_details.address.line2,
#                     county__iexact=shipping_details.address.state,
#                     grand_total=grand_total,
#                     original_bag=bag,
#                     stripe_pid=pid,
#                 )
#                 order_exists = True
#                 break
#             except Order.DoesNotExist:
#                 attempt += 1
#                 time.sleep(1)
#         if order_exists:
#             return HttpResponse(
#                 content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
#                 status=200)
#         else:
#             order = None
#             try:
#                 order = Order.objects.create(
#                     full_name=shipping_details.name,
#                     email=billing_details.email,
#                     phone_number=shipping_details.phone,
#                     country=shipping_details.address.country,
#                     postcode=shipping_details.address.postal_code,
#                     town_or_city=shipping_details.address.city,
#                     street_address1=shipping_details.address.line1,
#                     street_address2=shipping_details.address.line2,
#                     county=shipping_details.address.state,
#                     original_bag=bag,
#                     stripe_pid=pid,
#                 )
#                 for item_id, item_data in json.loads(bag).items():
#                     product = Product.objects.get(id=item_id)
#                     if isinstance(item_data, int):
#                         order_line_item = OrderLineItem(
#                             order=order,
#                             product=product,
#                             quantity=item_data,
#                         )
#                         order_line_item.save()
#                     else:
#                         for size, quantity in item_data['items_by_size'].items():
#                             order_line_item = OrderLineItem(
#                                 order=order,
#                                 product=product,
#                                 quantity=quantity,
#                                 product_size=size,
#                             )
#                             order_line_item.save()
#             except Exception as e:
#                 if order:
#                     order.delete()
#                 return HttpResponse(
#                     content=f'Webhook received: {event["type"]} | ERROR: {e}',
#                     status=500)
#         return HttpResponse(
#             content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook',
#             status=200)

#     def handle_payment_intent_payment_failed(self, event):
#         """
#         Handle the payment_intent.payment_failed webhook from Stripe
#         """
#         return HttpResponse(
#             content=f'Webhook received: {event["type"]}',
#             status=200)