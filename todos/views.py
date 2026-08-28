from django.shortcuts import render

from todos.queries import active_todos, resolved_todos


def home(request):
    """Render active and resolved TODOs on the application home page."""
    return render(
        request,
        "todos/home.html",
        {
            "active_todos": active_todos(),
            "resolved_todos": resolved_todos(),
        },
    )
