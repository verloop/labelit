from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from mainapp.models import Project, ProjectAnnotators, User
from mainapp.forms import CustomUserCreationForm, CustomUserChangeForm 

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('username', 'email', 'first_name', 'last_name','staff_type',)
    list_filter = ('username', 'email', 'first_name', 'last_name','staff_type',)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password',)}),
        ('Personal info', {'fields': ('first_name','last_name',)}),
        ('Permissions', {'fields': ('staff_type',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name','last_name', 'username', 'email', 'password1', 'password2', 'staff_type',)}
        ),
    )

    search_fields = ('email',)
    ordering = ('email',)

# Register your models here.
admin.site.register(Project)
admin.site.register(ProjectAnnotators)
admin.site.register(User, CustomUserAdmin)