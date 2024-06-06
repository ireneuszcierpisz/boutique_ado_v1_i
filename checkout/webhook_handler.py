"""
if the users intentionally or accidentally closes the browser window after the payment is confirmed 
but before the form is submitted we would end up with a payment in stripe but no order in our database. 
What's more, if we were building a real store that needed to complete post order operations like sending internal 
email notifications, none of that stuff would be triggered because the user never fully completed their order.
This could result in a customer being charged and never receiving a confirmation email or even worse never receiving
what they ordered.
We have to prevent this situation. Each time an event occurs on stripe such as a payment intent being created,
a payment being completed and so on stripe sends out what's called a webhook we can listen for.
Webhooks are like the signals django sends each time a model is saved or deleted except that they're sent securely
from stripe to a URL we specify.
		To handle these webhooks create custom class called StripeWH_Handler
"""        
from django.http import HttpResponse


class StripeWH_Handler:
    """Handle Stripe webhooks"""

    # use the __init__ method of the class, which is a setup method that's called every time an instance of the class
    # is created, to assign the request as an attribute of the class 
    # just in case we need to access any attributes of the request coming from stripe
    def __init__(self, request):
        self.request = request

    # take the event stripe is sending us
    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        # return an HTTP response indicating the event was received
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)