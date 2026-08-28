from django.urls import path

from todos import views

urlpatterns = [
    path("", views.home, name="home"),
    path("todos/create/", views.todo_create, name="todo-create"),
    path("todos/<int:pk>/edit/", views.todo_edit, name="todo-edit"),
    path(
        "todos/<int:pk>/edit/cancel/",
        views.todo_edit_cancel,
        name="todo-edit-cancel",
    ),
]
