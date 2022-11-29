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


class ProjectCreateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = (
            'name', 'dataset_format', 'dataset_path', 'config', 'export_format', "remote_export"
            )


class ProjectEditForm(forms.ModelForm):
    editable_fields = ('status', 'export_format')
    status_choice_values = [Project.Status.ACTIVE.value, Project.Status.DISABLED.value]
    class Meta:
        model = Project
        fields = (
            'name', 'dataset_format', 'dataset_path', 'config', 'status', 'export_format', 'remote_export'
            )

    def __init__(self, *args, **kwargs):
        super(ProjectEditForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            if field_name not in self.editable_fields:
                self.fields[field_name].disabled = True
        all_status_choices = self.fields['status'].choices
        self.fields['status'].choices = [choice for choice in all_status_choices
                                        if choice[0] in self.status_choice_values]


class AnnotatorSelectForm(forms.Form):
    annotators = forms.ModelMultipleChoiceField(
        widget = forms.CheckboxSelectMultiple,
        queryset = User.objects.filter(staff_type=User.StaffRole.ANNOTATOR),
        required=False
        )
