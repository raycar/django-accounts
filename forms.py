#from django import forms
from django import forms
from models import User
from django.contrib.auth.hashers import check_password
from django.utils.translation import ugettext as _

# Login
class LoginForm(forms.Form):
	username = forms.CharField(max_length=255, label=_("Username or Email"))
	password = forms.CharField(widget=forms.PasswordInput, label=_("Password"))

# Password reset
class PasswordResetEmailForm(forms.Form):
	email = forms.EmailField(max_length=255, label=_("Email"))

	def clean_email(self):
		email = self.cleaned_data['email']

		try:
			User.objects.get(email=email)
			return email
		except User.DoesNotExist:
			raise forms.ValidationError(_('Given email address not found in our database.'))

class PasswordResetForm(forms.Form):
	new_password = forms.CharField(widget=forms.PasswordInput, label=_("New password"))
	new_password_repeat = forms.CharField(widget=forms.PasswordInput, label=_("Repeat new password"))

	def clean(self):
		cleaned_data = super(PasswordResetForm, self).clean()

		if cleaned_data.get('new_password') != cleaned_data.get('new_password_repeat'):
			raise forms.ValidationError(
				_("Password and Password repeat fields do not match."))

		return cleaned_data

# Signup
class SignupForm(forms.ModelForm):
	password_repeat = forms.CharField(widget=forms.PasswordInput,
									  label=_("Repeat password"))

	def clean(self):
		cleaned_data = super(SignupForm, self).clean()

		password = cleaned_data.get('password')
		password_repeat = cleaned_data.get('password_repeat')
		if password != password_repeat:
			raise forms.ValidationError(
				_("Password and Password repeat fields do not match.")
			)

		return cleaned_data

	class Meta:
		model = User
		fields = ['email','password']
		widgets = {
			'password': forms.PasswordInput(),
		}

# Update
class UpdateForm(forms.ModelForm):
	username = forms.CharField(required=False)

	class Meta:
		model = User
		localized_fields = ('__all__')
		fields = ['username',
				  'first_name',
				  'last_name',
				  'email',
				  'email_privacy',
				  'birthdate',
				  'birthdate_privacy',
				  'gender',
				  'gender_privacy',
				  'country',
				  'country_privacy',
				  'city',
				  'city_privacy',
				  'address',
				  'address_privacy',
				  'postal_code',
				  'postal_code_privacy',
				  ]

# Email change
class ChangeEmailForm(forms.Form):
	current_password = forms.CharField(widget=forms.PasswordInput,
									   max_length=255,
									   label=_("Current password"))
	email = forms.EmailField(max_length=255, label=_("Email"))

	def __init__(self, *args, **kwargs):
		self.user_password = kwargs.pop('user_password', None)
		super(ChangeEmailForm, self).__init__(*args, **kwargs)

	def clean_current_password(self):
		current_password = self.cleaned_data['current_password']

		if not check_password(current_password, self.user_password):
			raise forms.ValidationError(_("Current password does not match."))

		return current_password

	def clean_email(self):
		new_email = self.cleaned_data['email']

		try:
			User.objects.get(email=new_email)
			raise forms.ValidationError(_('User with this Email address already exists'))
		except User.DoesNotExist:
			return new_email

# Password change
class ChangePasswordForm(forms.Form):
	current_password = forms.CharField(widget=forms.PasswordInput,
									   max_length=255,
									   label=_("Current password"))
	new_password = forms.CharField(widget=forms.PasswordInput, label=_("New password"))
	new_password_repeat = forms.CharField(widget=forms.PasswordInput, label=_("Repeat new password"))

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		super(ChangePasswordForm, self).__init__(*args, **kwargs)

	def clean_current_password(self):
		current_password = self.cleaned_data['current_password']

		if not check_password(current_password, self.user.password):
			raise forms.ValidationError(_("Current password does not match."))

		return current_password

	def clean(self):
		cleaned_data = super(ChangePasswordForm, self).clean()

		if cleaned_data.get('new_password') != cleaned_data.get('new_password_repeat'):
			raise forms.ValidationError(
				_("Password and Password repeat fields do not match."))

		return cleaned_data

# Deactivate
class DeleteForm(forms.Form):
	# requires required=True (True by default) to pass validation
	confirmation = forms.BooleanField(required=True,
									  label=_("Yes, I want to deactivate my account!"))