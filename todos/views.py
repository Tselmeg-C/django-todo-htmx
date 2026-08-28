from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from django.views.decorators.vary import vary_on_headers

from todos.forms import TodoForm
from todos.models import Todo
from todos.queries import active_todos, resolved_todos


def _is_htmx(request):
    return request.headers.get("HX-Request", "").lower() == "true"


def _todo_context(*, create_form=None, editing_todo=None, edit_form=None):
    if create_form is None:
        create_form = TodoForm()

    return {
        "active_todos": active_todos(),
        "resolved_todos": resolved_todos(),
        "create_form": create_form,
        "editing_todo": editing_todo,
        "edit_form": edit_form,
    }


def _render_todo_app(request, **context_overrides):
    return render(
        request,
        "todos/partials/todo_app.html",
        _todo_context(**context_overrides),
    )


def _render_todo_sections(request, *, editing_todo=None, edit_form=None):
    return render(
        request,
        "todos/partials/todo_sections.html",
        _todo_context(editing_todo=editing_todo, edit_form=edit_form),
    )


def home(request):
    """Render active and resolved TODOs on the application home page."""
    editing_todo = None
    edit_form = None
    editing_id = request.GET.get("edit")
    if editing_id:
        try:
            editing_pk = int(editing_id)
        except ValueError as exc:
            raise Http404("TODO not found") from exc
        editing_todo = get_object_or_404(Todo, pk=editing_pk)
        edit_form = TodoForm(instance=editing_todo)

    return render(
        request,
        "todos/home.html",
        _todo_context(editing_todo=editing_todo, edit_form=edit_form),
    )


@vary_on_headers("HX-Request")
@require_POST
def todo_create(request):
    form = TodoForm(request.POST)
    if form.is_valid():
        form.save()
        if _is_htmx(request):
            return _render_todo_app(request)
        return redirect("home")

    if _is_htmx(request):
        return _render_todo_app(request, create_form=form)
    return render(
        request,
        "todos/home.html",
        _todo_context(create_form=form),
    )


@vary_on_headers("HX-Request")
@require_http_methods(["GET", "POST"])
def todo_edit(request, pk):
    todo = get_object_or_404(Todo, pk=pk)

    if request.method == "GET":
        if _is_htmx(request):
            return _render_todo_sections(
                request,
                editing_todo=todo,
                edit_form=TodoForm(instance=todo),
            )
        return redirect(f"{reverse('home')}?edit={todo.pk}")

    form = TodoForm(request.POST, instance=todo)
    if form.is_valid():
        form.save()
        if _is_htmx(request):
            return _render_todo_sections(request)
        return redirect("home")

    if _is_htmx(request):
        return _render_todo_sections(
            request,
            editing_todo=todo,
            edit_form=form,
        )
    return render(
        request,
        "todos/home.html",
        _todo_context(editing_todo=todo, edit_form=form),
    )


@vary_on_headers("HX-Request")
@require_GET
def todo_edit_cancel(request, pk):
    get_object_or_404(Todo, pk=pk)
    if _is_htmx(request):
        return _render_todo_sections(request)
    return redirect("home")
