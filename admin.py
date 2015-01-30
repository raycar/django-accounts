from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from models import User
from forms import SignupForm, UpdateForm

class UserAdmin(AuthUserAdmin):
  fieldsets = (
    (None, {'fields': ('username', 'email', 'password',)}),
    ('Personal info', {'fields': ('first_name',
    							  'last_name',
    							  'birthdate',
    							  'gender')}),
    ('Location info', {'fields': ('address', 'postal_code', 'city', 'country')}),
    ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                    'groups', 'user_permissions')}),
    ('Important dates', {'fields': ('last_login', 'date_joined')}),
  )
  add_fieldsets = (
    (None, {'fields': ('email', 'password', 'password_repeat')}),
    ('Personal info', {'fields': ('first_name', 'last_name')}),
    ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
  )
  form = UpdateForm
  add_form = SignupForm
  list_display = ('username',
  				  'email',
  				  'first_name',
  				  'last_name',
  				  'is_active',
  				  'is_staff')
  list_editable = ('is_active',)
  list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
  search_fields = ('username', 'email', 'first_name', 'last_name')
  ordering = ('last_name','first_name',)

admin.site.register(User, UserAdmin)