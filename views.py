from django.shortcuts import render_to_response, redirect, get_list_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from forms import *
from models import User, PasswordResetRequest, EmailChangeRequest
import uuid

# Ajax specific
from cities_light.models import City
from django.http import HttpResponse
from django.core import serializers
import json

# Signin
def signin(request):
	form = LoginForm()

	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			user = authenticate(username=form.cleaned_data['username'],
								password=form.cleaned_data['password'])

			if user is not None:
				if user.is_active:
					login(request, user)

					msg = _("Hello, you are now logged in!")
					messages.add_message(request, messages.SUCCESS, msg)
					return redirect('home')
				else:
					try:
						# Reactivate and log user in if already registered
						confirm = user.emailchangerequest_set.get(
							type='registration', status='confirmed')
						user.is_active = True
						user.save()

						login(request, user)
						msg = _("Welcome back! We missed you while you were gone.")
						messages.add_message(request, messages.SUCCESS, msg)
					except EmailChangeRequest.DoesNotExist:
						msg = _(
							"You haven't confirmed your email yet. " \
							"Please check your email address for further instructions.")
						messages.add_message(request, messages.INFO, msg)

					return redirect('home')
			else:
				msg = _("Username/Email and Password do not match.")
				messages.add_message(request, messages.ERROR, msg)

	return render_to_response('signin.html', {'form': form},
		context_instance=RequestContext(request)
	)

# Signout
def signout(request):
	logout(request)

	msg = _("You have successfully logged out, see you soon!")
	messages.add_message(request, messages.SUCCESS, msg)
	return redirect('home')

# Signup
def create(request):
	form = SignupForm()
	if request.method == 'POST':
		form = SignupForm(request.POST)
		if form.is_valid():
			user = User.objects.create_user(form.cleaned_data['email'],
											form.cleaned_data['password'],
											request=request)

			msg = _("Your account was created successfully! \
				    Please check the given email address for further details \
				    on how to activate and use your account.")
			messages.add_message(request, messages.INFO, msg)
			return redirect('home')

	return render_to_response(
		'signup.html',
		{'form': form},
		context_instance=RequestContext(request)
	)

# Email change confirmation
def email_confirmation(request, email, hash_code):
	if email and hash_code:
		if EmailChangeRequest.objects.is_valid(email, hash_code):
			confirmation = EmailChangeRequest.objects.get_valid_object()
			user = confirmation.user

			if confirmation.type == 'registration':
				# Set user as active if is a registration
				user.is_active = True
			elif confirmation.type == 'request':
				# Update user email if is a email change request
				user.email = confirmation.email

			user.save()

			# Setting email confirmation as confirmed
			confirmation.status = 'confirmed'
			confirmation.save()

			# Set flash message and redirect home
			msg = _("Your email was successfully verified. You can now login!")
			messages.add_message(request, messages.SUCCESS, msg)
			return redirect('home')

	msg = _("We could not verify your email address. Please try again.")
	messages.add_message(request, messages.ERROR, msg)
	return redirect('home')

# Reset Password
def password_reset(request):
	form = PasswordResetEmailForm()

	if request.method == 'POST':
		form = PasswordResetEmailForm(request.POST)
		if form.is_valid():
			user = User.objects.get(email=form.cleaned_data['email'])
			user.reset_password(request)

			# Flash message
			msg = _("Please check your email account for further instructions.")
			messages.add_message(request, messages.INFO, msg)
			return redirect('home')

	return render_to_response(
		'password_reset.html',
		{'form': form},
		context_instance=RequestContext(request)
	)


# Reset password confirmation
def password_reset_confirmation(request, email, hash_code):
	if email and hash_code and PasswordResetRequest.objects.is_valid(email, hash_code):
		form = PasswordResetForm()

	else:
		msg = _("We could not verify your request. Please try again.")
		messages.add_message(request, messages.ERROR, msg)
		return redirect('home')

	# Form processing
	if request.method == 'POST':
		form = PasswordResetForm(request.POST)
		if form.is_valid():
			pw_reset = PasswordResetRequest.objects.get_valid_object()
			user = pw_reset.user
			user.set_password(form.cleaned_data['new_password'])
			user.save()

			# Set flash message and redirect home
			msg = _("Your password was successfully reset. You can now login!")
			messages.add_message(request, messages.SUCCESS, msg)
			return redirect('home')

	params = {'email': email, 'hash_code': hash_code}
	action_url = reverse('account:password-reset-confirmation', kwargs=params)

	return render_to_response(
		'password_reset_confirmation.html',
		{'form': form, 'action_url': action_url},
		context_instance=RequestContext(request)
	)


# Account Edit
@login_required
def update(request):
	user = request.user
	form = UpdateForm(instance=user)
	query = City.objects.filter(country_id=user.country) if user.country else City.objects.none()
	form.fields["city"].queryset = query

	if request.method == 'POST':
		form = UpdateForm(request.POST, instance=user)
		if form.is_valid():
			form.save()

			msg = _("Your profile was successfully updated.")
			messages.add_message(request, messages.SUCCESS, msg)
			return redirect('home')

	return render_to_response(
		'update.html',
		{'form': form},
		context_instance=RequestContext(request)
	)

# Account Email change
@login_required
def change_email(request):
	form = ChangeEmailForm()

	if request.method == 'POST':
		form = ChangeEmailForm(request.POST, user_password=request.user.password)
		if form.is_valid():
			user = request.user
			user.send_email_confirmation(form.cleaned_data['email'], request)

			# Flash message
			msg = _("Please check your inbox to confirm your new email address.")
			messages.add_message(request, messages.INFO, msg)
			return redirect('home')

	return render_to_response(
		'change_email.html',
		{'form': form},
		context_instance=RequestContext(request)
	)

@login_required
# Account Password change
def change_password(request):
	form = ChangePasswordForm()

	if request.method == 'POST':
		form = ChangePasswordForm(request.POST, user=request.user)
		if form.is_valid():
			user = request.user
			user.set_password(form.cleaned_data['new_password'])
			user.save()

			# Set flash message
			msg = _("Your password was successfully updated.")
			messages.add_message(request, messages.SUCCESS, msg)
			return redirect('home')

	return render_to_response(
		'change_password.html',
		{'form': form},
		context_instance=RequestContext(request)
	)

# Account eactivate
@login_required
def deactivate(request):
	form = DeleteForm()

	if request.method == 'POST':
		form = DeleteForm(request.POST)
		if form.is_valid():
			# Deactivate account
			user = request.user
			user.is_active = False
			user.save()

			# Logout
			logout(request)

			msg = _("Your account was disabled, we hope to see you again soon!")
			messages.add_message(request, messages.SUCCESS, msg)
			return redirect('home')
		else:
			msg = _("To delete your account you MUST confirm.")
			messages.add_message(request, messages.WARNING, msg)

	return render_to_response(
		'deactivate.html',
		{'form': form},
		context_instance=RequestContext(request)
	)


# Ajax requests
def cities(request, country_id):
	cities = get_list_or_404(City, country_id=country_id)
	data = serializers.serialize("json", cities)

	return HttpResponse(data, content_type='application/json')