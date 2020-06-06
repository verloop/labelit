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
    annotators_to_remove = forms.ModelMultipleChoiceField(
        widget = forms.CheckboxSelectMultiple,
        queryset = User.objects.all(),
        required=False
        )
    annotators_to_add = forms.ModelMultipleChoiceField(
        widget = forms.CheckboxSelectMultiple,
        queryset = User.objects.all(),
        required=False
        )
    def __init__(self, *args, **kwargs):
        self.annotator_assigned = kwargs.pop('annotator_assigned', None)
        self.annotators_not_assigned = kwargs.pop('annotators_not_assigned', None)
        super(AnnotatorSelectForm, self).__init__(*args, **kwargs)
        self.fields['annotators_to_remove'].queryset = self.annotator_assigned
        self.fields['annotators_to_add'].queryset = self.annotators_not_assigned