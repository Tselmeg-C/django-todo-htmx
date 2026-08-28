from django.shortcuts import render


def home(request):
    """Render the initial application shell."""
    return render(request, "todos/home.html")
