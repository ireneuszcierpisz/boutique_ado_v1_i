from django.shortcuts import render

# define a view which will render the bag template
def view_bag(request):
    """
    A view to return the bag contents page
    """
    return render(request, 'bag/bag.html')
