"""
Anytime stripe sends us a webhook letting us know that one of the events has occurred
our webhook function will be executed and we can handle the event however we need to.
"""

# gets settings file to get the webhook and the stripe API secrets
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from checkout.webhook_handler import StripeWH_Handler

import stripe

# The code for this function come directly from stripe with a couple modifications
@require_POST
@csrf_exempt
def webhook(request):
    """Listen for webhooks from Stripe"""
    # setup the webhook secret which will be used to verify that the webhook actually came from stripe
    wh_secret = settings.STRIPE_WH_SECRET
    # setup the stripe API key
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Get the webhook data and verify its signature
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
        payload, sig_header, wh_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    # a generic exception handler to catch any exceptions other than the two above stripe has provided
    except Exception as e:
        return HttpResponse(content=e, status=400)

    """ we can pass the event along to our webhook_handler.py 
    where is a convenient method written up for each type of webhook.
     """
    # Set up a webhook handler
    handler = StripeWH_Handler(request)

    # Map webhook events to relevant handler functions
    # the dictionarie's keys are the names of the webhooks coming from stripe
    # while its values are the actual methods inside the handler.
    event_map = {
        'payment_intent.succeeded': handler.handle_payment_intent_succeeded,
        'payment_intent.payment_failed': handler.handle_payment_intent_payment_failed,
    }

    # Get the webhook type from Stripe
    event_type = event['type']

    # If there's a handler for it, get it from the event_map
    # Use the generic one by default
    event_handler = event_map.get(event_type, handler.handle_event)

    # Call the event_handler with the event
    response = event_handler(event)

    # return the response to stripe
    return response


"""
        We don't have a way to determine in the webhook whether the user had the save info box checked.
        We can add that to the payment intent in a key called metadata, but 
        we have to do it from the server-side because the confirmCardPayment method in stripe_elements.js doesn't support adding it.
        We write cache_checkout_data view in checkout/views.py to take care of it.
"""