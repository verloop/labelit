from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Project

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('staff_type','email',)

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = UserChangeForm.Meta.fields


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = (
            'name', 'dataset_format', 'dataset_path', 'config', 'export_format'
            )

class AnnotatorSelectForm(forms.Form):
    annotators = forms.ModelMultipleChoiceField(
        widget = forms.CheckboxSelectMultiple,
        queryset = User.objects.all()
        )
    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset', None)
        super(AnnotatorSelectForm, self).__init__(*args, **kwargs)
        self.fields['annotators'].queryset = self.queryset