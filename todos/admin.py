from django.contrib import admin

from todos.models import Todo


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ("title", "due_date", "is_resolved")
    list_filter = ("is_resolved", "due_date")
    search_fields = ("title",)
