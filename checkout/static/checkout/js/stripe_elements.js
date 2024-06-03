/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/
// get the stripe public key and client secret from the checkout template using a little jQuery
var stripePublicKey  = $('#id_stripe_public_key').text().slice(1, -1);
// slice off the first and last character on each since the content of the elements have quotation marks which we don't want
// inspect checkout page to see: <script id="id_client_secret" type="application/json">"test client secret"</script>
var clientSecret = $('#id_client_secret').text().slice(1, -1);
// create variable stripe to set up Stripe (thanks to the stripe js script included in the base.html template)
var stripe = Stripe(stripePublicKey );
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
// mount the card element to the div in the form fieldset in checkout.html template
card.mount('#card-element');


// Handle realtime validation errors on the card element
// give functionality to the card element on checkout form
// add a listener on the card element for the change event
card.addEventListener('change', function (event) {
    // every time it changes we'll check to see if there are any errors
    var errorDiv = document.getElementById('card-errors');
    // display error in the card-errors div near the card-element div on the checkout.html
    if (event.error) {
        var html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${event.error.message}</span>
        `;
        $(errorDiv).html(html);
    } else {
        errorDiv.textContent = '';
    }
});


// Handle form submit
// get DOM element in checkout.html
var form = document.getElementById('payment-form');
// add a listener to the payment form's submit event; copy the code from the stripe documentation and make changes.
form.addEventListener('submit', function(ev) {
    // prevent default action which in our case is to POST.
    ev.preventDefault();
    // before calling out to stripe disable the card element and the submit button to prevent multiple submissions
    card.update({ 'disabled': true});
    $('#submit-button').attr('disabled', true);
    // use the stripe.confirmCardPayment method to send the card information securely to stripe
    stripe.confirmCardPayment(clientSecret, {
        // call the confirm card payment method
        payment_method: {
            // provide the card to stripe
            card: card,
        }
    // then execute this function on the result
    }).then(function(result) {
        // If there's an error put the error message right into the card error div.
        if (result.error) {
            var errorDiv = document.getElementById('card-errors');
            var html = `
                <span class="icon" role="alert">
                <i class="fas fa-times"></i>
                </span>
                <span>${result.error.message}</span>`;
            $(errorDiv).html(html);
            // re-enable the card element and the submit button to allow the user to fix the error
            card.update({ 'disabled': false});
            $('#submit-button').attr('disabled', false);
        } else {
            // If the status of the payment intent comes back is succeeded we'll submit the form.
            if (result.paymentIntent.status === 'succeeded') {
                form.submit();
            }
        }
    });
});