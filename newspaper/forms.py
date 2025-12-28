from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import Article, Topic

Redactor = get_user_model()


class TopicSearchForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search by name"}),
    )


class RedactorSearchForm(forms.Form):
    username = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search by username"}),
    )


class RedactorCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Redactor
        fields = UserCreationForm.Meta.fields + (
            "years_of_experience",
            "first_name",
            "last_name",
        )

    def clean_years_of_experience(self):
        return validate_years_of_experience(
            self.cleaned_data["years_of_experience"]
        )


class RedactorUpdateForm(forms.ModelForm):
    class Meta:
        model = Redactor
        fields = ["username","years_of_experience", "first_name", "last_name",]

    def clean_years_of_experience(self):
        return validate_years_of_experience(
            self.cleaned_data["years_of_experience"]
        )


def validate_years_of_experience(years):
    if years < 0:
        raise ValidationError("Experience cannot be negative.")
    if years > 50:
        raise ValidationError(
            "Experience seems too high. Please check the value."
        )
    return years


class ArticleSearchForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search by title..."}),
    )


class ArticleForm(forms.ModelForm):
    topics = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        label="Select Topics",
    )

    publishers = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        label="Co-authors (Admin only)",
    )

    class Meta:
        model = Article
        fields = ["title", "content", "topics", "publishers"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter article title...",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 20,
                    "placeholder": "Write your content here...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        can_edit_publishers = False

        if user and user.is_authenticated:
            if user.is_superuser:
                can_edit_publishers = True
            elif self.instance.pk:
                can_edit_publishers = user in self.instance.publishers.all()

            if field := self.fields.get("publishers"):
                field.queryset = field.queryset.exclude(id=user.id)
                field.label_from_instance = lambda obj: obj.username

        if not can_edit_publishers:
            del self.fields["publishers"]
