from django.shortcuts import render

# Create your views here.
# define an index view which will render the index template
def index(request):
    """
    A view to return the index page
    """
    return render(request, 'home/index.html')
