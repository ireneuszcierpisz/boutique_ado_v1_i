from django.shortcuts import render, redirect

# define a view which will render the bag template
def view_bag(request):
    """
    A view to return the bag contents page
    """
    return render(request, 'bag/bag.html')


# We'll submit the form to this view including the product id and the quantity
def add_to_bag(request, item_id):
    """ Add a quantity of the specified product to the shopping bag """

    # get the quantity from the form
    # convert it to an integer since it'll come from the template as a string
    quantity = int(request.POST.get('quantity'))

    # get the redirect URL from the form, so we know where to redirect once the process here is finished
    redirect_url = request.POST.get('redirect_url')

    # HTTP every request-response cycle between the server and the client, 
    # in our case between the django view on the server-side and our form making the request on the client-side,
    # uses what's called a session, to allow information to be stored until the client and server are done communicating.
    # It allows to store the contents of the shopping bag in the HTTP session, while the user browses the site 
    # and adds items to be purchased, by storing the shopping bag in the session. It will persist until the user closes their browser.
    # A variable bag accesses the requests session and first check if there's a 'bag' variable in the session
    # and if not we'll create one as an empty dictionary
    bag = request.session.get('bag', {})

    # add the item to the bag
    # if there's already a key in the bag dictionary matching product id, increment its quantity
    if item_id in list(bag.keys()):
        bag[item_id] += quantity
    else:
        # create a key of the items id and set it equal to the quantity
        bag[item_id] = quantity

    # put the bag variable into the session which itself is a python dictionary
    request.session['bag'] = bag

    # print the shopping bag from the session to the console
    print(request.session['bag'])

    # redirect the user back to the redirect_url
    return redirect(redirect_url)