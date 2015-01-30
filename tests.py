from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.core import mail
from django.contrib.auth.hashers import check_password
from models import User

# Create your tests here.
class UserTest(TestCase):
	def setUp(self):
		self.c = Client()

		# Create user
		self.username = 'test_user'
		self.password = '123123'
		self.email = 'test_user@localhost.com'
		self.user = User.objects.create_user(self.email, self.password)
		self.user.username = self.username
		self.user.is_active = True
		self.user.save()

	def test_reset_password(self):
		# Check email validations works for unknown addresses
		data = {'email': 'unexistentemail@example.com'}
		response = self.c.post(reverse('account:password-reset'), data, follow=True)
		self.assertContains(response, 'Given email address not found in our database')

		# Inserting a valid email
		data = {'email': self.email}
		response = self.c.post(reverse('account:password-reset'), data, follow=True)
		self.assertContains(response, 'check your email account')

		# Check if mail was sent
		self.assertEquals(len(mail.outbox), 1)
		self.assertEquals(mail.outbox[0].to, [self.email,])
		self.assertEquals(mail.outbox[0].subject, 'Reset password')

		# Confirm email with wrong hash
		response = self.c.get(
			reverse('account:password-reset-confirmation',
				kwargs={'email': self.email,
						'hash_code': 'abcdef1234'}), follow=True)
		self.assertContains(response, 'could not verify your request')

		# Confirm email with given hash_code
		user = User.objects.get(email=self.email)
		pw_request = user.passwordresetrequest_set.all()[0]

		response = self.c.get(
			reverse('account:password-reset-confirmation',
				kwargs={'email': self.email,
						'hash_code': pw_request.hash_code}), follow=True)
		self.assertEquals(response.status_code, 200)

		# Check password reset form validations
		new_password = '456456'
		data = {'new_password': new_password, 'new_password_repeat': '000'}
		response = self.c.post(
			reverse('account:password-reset-confirmation',
				kwargs={'email': self.email,
						'hash_code': pw_request.hash_code}), data, follow=True)
		self.assertContains(response, 'repeat fields do not match')

		# Check password reset form works
		data = {'new_password': new_password, 'new_password_repeat': new_password}
		response = self.c.post(
			reverse('account:password-reset-confirmation',
				kwargs={'email': self.email,
						'hash_code': pw_request.hash_code}), data, follow=True)
		self.assertContains(response, 'successfully reset')

		# user should now have the new password
		user = User.objects.get(email=self.email)
		self.assertTrue(check_password(new_password, user.password))

	def test_create_user_validations(self):
		# Failed authentication
		user_email = 'ThisIsNotAnEmailAddress'
		user_passw = '123123'
		data = {'email': user_email,
				'password': user_passw,
				'password_repeat': 'ThisShouldNotMatchPW'}
		response = self.c.post(reverse('account:signup'), data, follow=True)
		self.assertContains(response, 'fields do not match')
		self.assertContains(response, 'valid email')

		# Success creation
		data['email'] = 'test@example.com'
		data['password_repeat'] = user_passw
		response = self.c.post(reverse('account:signup'), data, follow=True)
		self.assertContains(response, 'created successfully')

		# Check if mail was sent
		self.assertEquals(len(mail.outbox), 1)
		self.assertEquals(mail.outbox[0].to, [data['email'],])
		self.assertEquals(mail.outbox[0].subject, 'Email confirmation')

		user = User.objects.get(email=data['email'])
		email_confirm = user.emailchangerequest_set.all()[0]

		# Confirm email with wrong hash
		response = self.c.get(
			reverse('account:email-confirmation',
				kwargs={'email': user.email,
						'hash_code': 'abcdef1234'}), follow=True)
		self.assertContains(response, 'could not verify your email address')

		# Confirm email with given hash_code
		self.assertFalse(user.is_active)
		response = self.c.get(
			reverse('account:email-confirmation',
				kwargs={'email': user.email,
						'hash_code': email_confirm.hash_code}), follow=True)
		self.assertContains(response, 'successfully verified')

		# user should now be active
		user = User.objects.get(email=data['email'])
		self.assertTrue(user.is_active)

	def test_login(self):
		# Setting user inactive
		self.user.is_active = False
		self.user.save()

		# Failed authentication - wrong credentials
		data = {'username': self.email, 'password': 'WrongPassword'}
		response = self.c.post(reverse('account:signin'), data, follow=True)
		self.assertContains(response, 'do not match.')

		# Successful authentication
		# Setting user active again
		self.user.is_active = True
		self.user.save()

		# Logging in
		data = {'username': self.email,
				'password': self.password,
				'redirect_url': reverse('account:signin')
		}
		response = self.c.post(reverse('account:signin'), data, follow=True)
		self.assertContains(response, 'now logged in')

		# To be implemented:
		# Check if redirected to form's 'redirect_url' field
		self.assertRedirects(response, reverse('home'))

		# Check fi user is redirected to home page
		self.assertRedirects(response, reverse('home'))

		# Logout
		response = self.c.get(reverse('account:signout'), follow=True)
		self.assertRedirects(response, reverse('home'))
		self.assertContains(response, 'see you soon')

	def test_user_edit_works(self):
		# Check all values are as expected
		user = self.user
		self.assertEquals(self.username, user.username)
		self.assertIsNone(user.first_name)
		self.assertIsNone(user.last_name)
		self.assertIsNone(user.gender)

		# Successful authentication with active user
		self.c.login(username=self.email, password=self.password)

		# Set new values and send them as post
		username, first_name, last_name, gender = 'jdoe','John', 'Doe', 'male'
		data = {'username': username,
				'first_name': first_name,
				'last_name': last_name,
				'gender': gender,
				'email': self.email,
				'email_privacy': 'friends',
				'birthdate_privacy': 'friends',
				'gender_privacy': 'friends',
				'country_privacy': 'friends',
				'city_privacy': 'friends',
				'address_privacy': 'friends',
				'postal_code_privacy': 'friends',
		}
		response = self.c.post(reverse('account:update'), data, follow=True)
		self.assertRedirects(response, reverse('home'))
		self.assertContains(response, 'successfully updated')

		user2 = User.objects.get(pk=self.user.id)
		self.assertEquals(username, user2.username)
		self.assertEquals(first_name, user2.first_name)
		self.assertEquals(last_name, user2.last_name)
		self.assertEquals(gender, user2.gender)

	def test_user_email_change(self):
		# Authentication user
		self.c.login(username=self.email, password=self.password)

		# Validation checkup
		new_email = 'new_test_email@localhost.com'
		data = {'current_password': 'WrongPassword', 'email': self.email}
		response = self.c.post(reverse('account:change_email'), data, follow=True)
		self.assertEquals(200, response.status_code)
		self.assertContains(response, 'Current password does not match')
		self.assertContains(response, 'Email address already exists')

		# Change email
		data = {'current_password': self.password, 'email': new_email}
		response = self.c.post(reverse('account:change_email'), data, follow=True)
		self.assertRedirects(response, reverse('home'))
		self.assertContains(response, 'check your inbox')

		# Old user email shall still work while the new is not confirmed
		user = User.objects.get(email=self.email)
		self.assertEquals(self.email, user.email)

		# Check if mail was sent
		self.assertEquals(len(mail.outbox), 1)
		self.assertEquals(mail.outbox[0].to, [data['email'],])
		self.assertEquals(mail.outbox[0].subject, 'Email confirmation')

		# Confirm and use the new email address
		confirmation = self.user.emailchangerequest_set.all()[0]
		self.assertEquals(new_email, confirmation.email)

		response = self.c.post(
			reverse('account:email-confirmation',
				kwargs={'email': confirmation.email,
						'hash_code': confirmation.hash_code}), follow=True)
		self.assertContains(response, 'successfully verified')

		# user should now have the new email address
		user = User.objects.get(email=new_email)
		self.assertEquals(new_email, user.email)

	def test_user_password_change(self):
		# Authentication user
		self.c.login(username=self.email, password=self.password)

		# Validation check: wrong current password
		new_pw = '987987'
		data = {
			'current_password': 'WrongPassword',
			'new_password': new_pw,
			'new_password_repeat': 'new_pw'
		}
		response = self.c.post(reverse('account:change_password'), data, follow=True)
		#print response
		self.assertContains(response, 'Current password does not match')
		self.assertContains(response, 'Password and Password repeat fields do not match')

		# Change password
		data = {
			'current_password': self.password,
			'new_password': new_pw,
			'new_password_repeat': new_pw
		}
		response = self.c.post(reverse('account:change_password'), data, follow=True)
		self.assertRedirects(response, reverse('home'))
		self.assertContains(response, 'password was successfully updated')

		# Confirm user has an updated password
		user = User.objects.get(email=self.email)
		self.assertTrue(check_password(new_pw, user.password))

	def test_user_account_deactivation_and_reactivation_works(self):
		# Authentication user
		self.c.login(username=self.email, password=self.password)

		# confirmation=False, show a warning message
		data = {'confirmation': False}
		response = self.c.post(reverse('account:deactivate'), data, follow=True)
		self.assertEquals(response.status_code, 200)
		self.assertContains(response, 'you MUST confirm')

		# confirmation=True, user should be deactivated and logged out
		data = {'confirmation': True}
		response = self.c.post(reverse('account:deactivate'), data, follow=True)
		self.assertRedirects(response, reverse('home'))
		self.assertContains(response, 'hope to see you again soon')

		# Update user object
		user = User.objects.get(email=self.email)
		self.assertFalse(user.is_active)

		# Reactivation should not work when user has never confirmed
		# the registration email address
		data = {'username': self.email, 'password': self.password}
		response = self.c.post(reverse('account:signin'), data, follow=True)
		self.assertContains(response, 'confirmed your email yet')

		# Reactivation with confirmed user email
		confirm = self.user.emailchangerequest_set.create(
			email=self.email, hash_code='something1', type='registration', status='confirmed')
		confirm.save()

		data = {'username': self.email, 'password': self.password}
		response = self.c.post(reverse('account:signin'), data, follow=True)
		self.assertContains(response, 'Welcome back! We missed you')

		# Update user object
		user = User.objects.get(email=self.email)
		self.assertTrue(user.is_active)