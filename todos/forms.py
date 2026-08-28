from django import forms

from todos.models import Todo


class TodoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Keep validation messages programmatically associated with their
        # controls when the form is rendered after an invalid submission.
        for field in self.visible_fields():
            field.field.widget.attrs.setdefault(
                "aria-describedby", f"{field.auto_id}-error"
            )

    class Meta:
        model = Todo
        fields = ("title", "description", "due_date")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }
