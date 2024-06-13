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
        # print out the payment intent coming from stripe once the user makes a payment; 
        # it should have a metadata attached
        intent = event.data.object
        print(intent)

        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)


    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)