/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/
// get the stripe public key and client secret from the checkout template using a little jQuery
var stripe_public_key = $('#id_stripe_public_key').text().slice(1, -1);
// slice off the first and last character on each since the content of the elements have quotation marks which we don't want
// inspect checkout page to see: <script id="id_client_secret" type="application/json">"test client secret"</script>
var client_secret = $('#id_client_secret').text().slice(1, -1);
// create variable stripe to set up Stripe (thanks to the stripe js script included in the base.html template)
var stripe = Stripe(stripe_public_key);
// create an instance of stripe elements
var elements = stripe.elements();
// get basic styles from the stripe js Docs
var style = {
    base: {
        color: '#000',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
            color: '#aab7c4'
        }
    },
    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545'
    }
};
// create a card element which accept a style argument
var card = elements.create('card', {style: style});
// mount the card element to the div in the form fieldset in checkout template
card.mount('#card-element');