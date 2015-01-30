from django.db import models
from django.core import validators
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.conf import settings
from django.core.urlresolvers import reverse
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from cities_light.models import Country, City
import re
import uuid

class UserManager(BaseUserManager):
	def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
		now = timezone.now()

		# Get and remove extra params from extra_fields
		if 'request' in extra_fields:
			request = extra_fields['request']
			del extra_fields['request']
		else:
			request = None

		# Create user
		email = self.normalize_email(email)
		user = self.model(email=email,
			is_staff=is_staff, is_active=False,
			is_superuser=is_superuser, last_login=now,
			date_joined=now, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)

		# Confirm user's email address
		if request:
			user.send_email_confirmation(user.email, request, 'registration')

		return user

	def create_user(self, email=None, password=None, **extra_fields):
		return self._create_user(email, password, False, False, **extra_fields)

	def create_superuser(self, email, password, **extra_fields):
		user=self._create_user(email, password, True, True, **extra_fields)
		user.is_active=True
		user.save(using=self._db)
		return user

class User(AbstractBaseUser, PermissionsMixin):
	# Set manager
	objects = UserManager()

	# Model Fields
	privacy_choices = (
		('public', _('Public')),
		('friends', _('Friends')),
		('me', _('Only me')),
	)

	gender_choices = (
		('male', _('Male')),
		('female',_('Female'))
	)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = []

	username = models.CharField(
		_('username'),
		max_length=30,
		unique=True,
		null=True,
		help_text=_('Required. 30 characters or fewer. Letters, numbers and @/./+/-/_ characters'),
		validators=[
			validators.RegexValidator(re.compile('^[\w.@+-]+$'), _('Enter a valid username.'), _('invalid'))
		]
	)

	first_name = models.CharField(_('first name'),
								  max_length=30,
								  blank=True,
								  null=True)
	last_name = models.CharField(_('last name'),
								 max_length=30,
								 blank=True,
								 null=True)
	email = models.EmailField(_('email address'),
							  max_length=255,
							  unique=True)
	is_staff = models.BooleanField(_('staff status'),
								   default=False,
								   help_text=_('Designates whether the user can log into this admin site.'))
	is_active = models.BooleanField(_('active'),
									default=False,
									help_text=_('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'))
	date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

	# End of Django's base user model fields and beginning of custom fields

	email_privacy = models.CharField(max_length=50,
									 choices=privacy_choices,
									 default='friends')
	birthdate = models.DateField(blank=True, null=True)
	birthdate_privacy = models.CharField(max_length=50,
										 choices=privacy_choices,
										 default='friends')
	gender = models.CharField(max_length=50, choices=gender_choices, null=True)
	gender_privacy = models.CharField(max_length=50, choices=privacy_choices,
									  default='friends')
	# Location specific
	country = models.ForeignKey(Country,
								verbose_name=_('Country'),
								blank=True,
								null=True)
	country_privacy = models.CharField(max_length=50,
									   choices=privacy_choices,
									   default='friends')
	city = models.ForeignKey(City, verbose_name=_('City'), blank=True, null=True)
	city_privacy = models.CharField(max_length=50,
									choices=privacy_choices,
									default='friends')
	address = models.CharField(max_length=255,
							   blank=True,
							   null=True)
	address_privacy = models.CharField(max_length=50,
									   choices=privacy_choices,
									   default='friends')
	postal_code = models.CharField(max_length=255,
								   blank=True,
								   null=True)
	postal_code_privacy = models.CharField(max_length=50,
										   choices=privacy_choices,
										   default='friends')

	class Meta:
		verbose_name = _('user')
		verbose_name_plural = _('users')

	def get_full_name(self):
		full_name = '%s %s' % (self.first_name, self.last_name)
		return full_name.strip()

	def get_short_name(self):
		return self.first_name

	def email_user(self, subject, message, from_email=None):
		send_mail(subject, message, from_email, [self.email])

	def send_email_confirmation(self, email, request, type='request'):
		change_request = self.emailchangerequest_set.create(
			email=UserManager.normalize_email(email),
			hash_code=uuid.uuid1().hex[:10],
			type=type)

		confirmation_url = request.build_absolute_uri(
			reverse('account:email-confirmation', kwargs={
					'email': change_request.email,
					'hash_code': change_request.hash_code}))

		context = {'user': self, 'confirmation_url': confirmation_url}
		# Txt content
		email = EmailMultiAlternatives(
			'Email confirmation', # Subject
			render_to_string('email/confirmation.txt', context), #txt content
			settings.DEFAULT_FROM_EMAIL,
			[change_request.email,])

		# HTML content
		email.attach_alternative(
			render_to_string('email/confirmation.html', context), "text/html")
		email.send()

	def reset_password(self, request):
		# Send reset email to confirm
		reset_pw = self.passwordresetrequest_set.build(user=self)
		confirmation_url = request.build_absolute_uri(
			reverse('account:password-reset-confirmation', kwargs={
					'email': self.email, 'hash_code': reset_pw.hash_code}))

		context = {'email': self.email, 'confirmation_url': confirmation_url}
		txt_content = render_to_string('email/password_reset.txt', context)
		html_content = render_to_string('email/password_reset.html', context)

		subject = 'Reset password'
		email = EmailMultiAlternatives(
			subject, txt_content, settings.DEFAULT_FROM_EMAIL, [self.email,])
		email.attach_alternative(html_content, "text/html")
		email.send()

class ContactEmail(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	privacy = models.CharField(max_length=50, choices=User.privacy_choices,
							   default="friends")
	email = models.EmailField(max_length=255, unique=True)
	create_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	class Meta():
		db_table = "accounts_user_contact_email"

class ContactPhone(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	privacy = models.CharField(max_length=50, choices=User.privacy_choices,
							   default="friends")
	country_code = models.IntegerField(max_length=255, unique=True)
	number = models.IntegerField(max_length=255, unique=True)
	create_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	class Meta():
		db_table = "accounts_user_contact_phone"

# Password reset
class PasswordResetRequestManager(models.Manager):
	def build(self, user):
		return self.create(
			user=user, hash_code=uuid.uuid1().hex[:10], status='pending')

	def is_valid(self, email, hash_code):
		try:
			obj = self.order_by('-created_at').get(user__email=email,
												   hash_code=hash_code)

			# Fall back to 7 days, if no settings are found
			try:
				expiration_date = timezone.timedelta(days=settings.EMAIL_CONFIRM_EXPIRY_DAYS)
			except Exception:
				expiration_date = timezone.timedelta(days=7)

			expiration_date = obj.created_at + expiration_date
			if timezone.now() <= expiration_date:
				self.obj = obj
				return True

		except PasswordResetRequest.DoesNotExist:
			return False

	def get_valid_object(self):
		return self.obj

class PasswordResetRequest(models.Model):
	# Set manager
	objects = PasswordResetRequestManager()

	# Model Fields
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	hash_code = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	status = models.CharField(max_length=255, default='pending')

	class Meta():
		# For v1.7+ >
		#default_related_name = "email_confirmation"
		ordering = ['-created_at']
		get_latest_by = "created_at"
		db_table = "accounts_user_password_reset_request"

# Email confirmation: Manager & Models
class EmailChangeRequestManager(models.Manager):
	types = ('registration', 'request')

	def build(self, user, email, type=None):
		if type is None:
			type = 'request'
		elif type.lower() not in self.types:
			raise AttributeError('Unknown type received: %s.' % type)

		return self.create(
			user=user,
			email=email,
			hash_code=uuid.uuid1().hex[:10],
			type=type
		)

	def is_valid(self, email, hash_code):
		try:
			obj = self.order_by('-created_at').get(email=email, hash_code=hash_code)

			# Fall back to 7 days, if no settings are found
			try:
				expiration_date = timezone.timedelta(days=settings.EMAIL_CONFIRM_EXPIRY_DAYS)
			except Exception:
				expiration_date = timezone.timedelta(days=7)

			expiration_date = obj.created_at + expiration_date
			if timezone.now() <= expiration_date or obj.type == 'registration':
				self.obj = obj
				return True

		except EmailChangeRequest.DoesNotExist:
			return False

	def get_valid_object(self):
		return self.obj

class EmailChangeRequest(models.Model):
	# Set manager
	objects = EmailChangeRequestManager()

	# Model Fields
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	email = models.EmailField(max_length=255)
	hash_code = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	type = models.CharField(max_length=255, default='request')
	status = models.CharField(max_length=255, default='pending')

	class Meta():
		# For v1.7+ >
		#default_related_name = "email_confirmation"
		ordering = ['-created_at']
		get_latest_by = "created_at"
		db_table = "accounts_user_email_change_request"