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
    path("todos/<int:pk>/resolve/", views.todo_resolve, name="todo-resolve"),
    path("todos/<int:pk>/reopen/", views.todo_reopen, name="todo-reopen"),
    path(
        "todos/<int:pk>/delete/confirm/",
        views.todo_delete_confirm,
        name="todo-delete-confirm",
    ),
    path(
        "todos/<int:pk>/delete/cancel/",
        views.todo_delete_cancel,
        name="todo-delete-cancel",
    ),
    path("todos/<int:pk>/delete/", views.todo_delete, name="todo-delete"),
]
