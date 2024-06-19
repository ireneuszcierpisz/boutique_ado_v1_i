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
// add a listener to the payment form's submit event; (copy the code from the stripe documentation and make changes)
form.addEventListener('submit', function(ev) {
    // When the user clicks the submit button the event listener prevents the form from submitting
    // prevent default action which in our case is to POST.
    ev.preventDefault();
    //and instead of submiting disables the card element and triggers the loading overlay.
    // (before calling out to stripe disable the card element and also the submit button to prevent multiple submissions)
    card.update({ 'disabled': true});
    $('#submit-button').attr('disabled', true);
    // trigger the overlay and fade out the form (when the user clicks the submit button)
    $('#payment-form').fadeToggle(100);
    $('#loading-overlay').fadeToggle(100);

    /*    
        Create the variables to capture the form data we can't put in the payment intent here
        and instead post it to the cache_checkout_data view    
    */
    // get the boolean value of the saved info box by looking at its checked attribute
    // #id-save-info input element in checkout.html
    var saveInfo = Boolean($('#id-save-info').attr('checked'));
    // From using {% csrf_token %} in the form;
    // get the CSRF token from the input that Django generates on our form
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
    // create an object to pass above information to the new view
    // and pass the client secret for the payment intent
    var postData = {
        'csrfmiddlewaretoken': csrfToken,
        'client_secret': clientSecret,
        'save_info': saveInfo,
    };
    // create the url variable for cache_checkout_data URL
    var url = '/checkout/cache_checkout_data/';
    
    // Use the post method built into jQuery to post the postData to the view
    // telling it we're posting to the url and that we want to post the postData above.
    // As we want to wait for a response that the payment intent was updated, before calling the confirmed payment method 
    // so we tacking on the .done method 
    // and executing the callback function which will be executed if cache_checkout_data view returns a 200 response
    $.post(url, postData).done(function () {
        /* The cache_checkout_data view updates the payment intent and returns a 200 response, at which point we
           call the confirmCardPayment method from stripe and if everything is ok submit the form */
    // use the stripe.confirmCardPayment method to send the card information securely to stripe
        stripe.confirmCardPayment(clientSecret, {
            // call the confirm card payment method
            payment_method: {
                // provide the card to stripe
                card: card,
                billing_details: {
                    // The same fields we've got in our form so add all this in getting the data from our form 
                    // and using the trim method to strip off any excess whitespace.
                    name: $.trim(form.full_name.value),
                    phone: $.trim(form.phone_number.value),
                    email: $.trim(form.email.value),
                    address:{
                        line1: $.trim(form.street_address1.value),
                        line2: $.trim(form.street_address2.value),
                        city: $.trim(form.town_or_city.value),
                        country: $.trim(form.country.value),
                        state: $.trim(form.county.value),
                    }
                }
            },
            shipping: {
                name: $.trim(form.full_name.value),
                phone: $.trim(form.phone_number.value),
                address: {
                    line1: $.trim(form.street_address1.value),
                    line2: $.trim(form.street_address2.value),
                    city: $.trim(form.town_or_city.value),
                    country: $.trim(form.country.value),
                    // only added postcode to the shipping since the billing postal code will come from the card element 
                    // and stripe will override it if we try to add it at billing_details
                    postal_code: $.trim(form.postcode.value),
                    state: $.trim(form.county.value),
                }
            },

        /*
        We don't have a way to determine in the webhook whether the user had the save info box checked.
        We can add that to the payment intent in a key called metadata, but 
        we have to do it from the server-side because the confirmCardPayment method here doesn't support adding it.
        We write cache_checkout_data view in checkout/views.py to take care of it.
        */

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
                //If there's an error in the form   then the error will be displayed for the user
                $(errorDiv).html(html);
                
                $('#payment-form').fadeToggle(100);
                //   then the loading overlay will be hidden
                $('#loading-overlay').fadeToggle(100);
                //   then the card element will be re-enabled
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
    /*   If anything goes wrong posting the data to cache_checkout_data view we'll reload the page and
         display the error without ever charging the user */
    // failure function, which will be triggered if cache_checkout_data view sends a 400 bad request response 
    }).fail(function () {
        // in that case, just reload the page to show the user the django error message from the view
        location.reload();
    })
});




// /*
//     Core logic/payment flow for this comes from here:
//     https://stripe.com/docs/payments/accept-a-payment

//     CSS from here: 
//     https://stripe.com/docs/stripe-js
// */

// var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
// var clientSecret = $('#id_client_secret').text().slice(1, -1);
// var stripe = Stripe(stripePublicKey);
// var elements = stripe.elements();
// var style = {
//     base: {
//         color: '#000',
//         fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
//         fontSmoothing: 'antialiased',
//         fontSize: '16px',
//         '::placeholder': {
//             color: '#aab7c4'
//         }
//     },
//     invalid: {
//         color: '#dc3545',
//         iconColor: '#dc3545'
//     }
// };
// var card = elements.create('card', {style: style});
// card.mount('#card-element');

// // Handle realtime validation errors on the card element
// card.addEventListener('change', function (event) {
//     var errorDiv = document.getElementById('card-errors');
//     if (event.error) {
//         var html = `
//             <span class="icon" role="alert">
//                 <i class="fas fa-times"></i>
//             </span>
//             <span>${event.error.message}</span>
//         `;
//         $(errorDiv).html(html);
//     } else {
//         errorDiv.textContent = '';
//     }
// });

// // Handle form submit
// var form = document.getElementById('payment-form');

// form.addEventListener('submit', function(ev) {
//     ev.preventDefault();
//     card.update({ 'disabled': true});
//     $('#submit-button').attr('disabled', true);
//     $('#payment-form').fadeToggle(100);
//     $('#loading-overlay').fadeToggle(100);

//     var saveInfo = Boolean($('#id-save-info').attr('checked'));
//     // From using {% csrf_token %} in the form
//     var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
//     var postData = {
//         'csrfmiddlewaretoken': csrfToken,
//         'client_secret': clientSecret,
//         'save_info': saveInfo,
//     };
//     var url = '/checkout/cache_checkout_data/';

//     $.post(url, postData).done(function () {
//         stripe.confirmCardPayment(clientSecret, {
//             payment_method: {
//                 card: card,
//                 billing_details: {
//                     name: $.trim(form.full_name.value),
//                     phone: $.trim(form.phone_number.value),
//                     email: $.trim(form.email.value),
//                     address:{
//                         line1: $.trim(form.street_address1.value),
//                         line2: $.trim(form.street_address2.value),
//                         city: $.trim(form.town_or_city.value),
//                         country: $.trim(form.country.value),
//                         state: $.trim(form.county.value),
//                     }
//                 }
//             },
//             shipping: {
//                 name: $.trim(form.full_name.value),
//                 phone: $.trim(form.phone_number.value),
//                 address: {
//                     line1: $.trim(form.street_address1.value),
//                     line2: $.trim(form.street_address2.value),
//                     city: $.trim(form.town_or_city.value),
//                     country: $.trim(form.country.value),
//                     postal_code: $.trim(form.postcode.value),
//                     state: $.trim(form.county.value),
//                 }
//             },
//         }).then(function(result) {
//             if (result.error) {
//                 var errorDiv = document.getElementById('card-errors');
//                 var html = `
//                     <span class="icon" role="alert">
//                     <i class="fas fa-times"></i>
//                     </span>
//                     <span>${result.error.message}</span>`;
//                 $(errorDiv).html(html);
//                 $('#payment-form').fadeToggle(100);
//                 $('#loading-overlay').fadeToggle(100);
//                 card.update({ 'disabled': false});
//                 $('#submit-button').attr('disabled', false);
//             } else {
//                 if (result.paymentIntent.status === 'succeeded') {
//                     form.submit();
//                 }
//             }
//         });
//     }).fail(function () {
//         // just reload the page, the error will be in django messages
//         location.reload();
//     })
// });