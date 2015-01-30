# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import re
import django.utils.timezone
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('cities_light', '0002_city'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(null=True, max_length=30, validators=[django.core.validators.RegexValidator(re.compile(b'^[\\w.@+-]+$'), 'Enter a valid username.', 'invalid')], help_text='Required. 30 characters or fewer. Letters, numbers and @/./+/-/_ characters', unique=True, verbose_name='username')),
                ('first_name', models.CharField(max_length=30, null=True, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, null=True, verbose_name='last name', blank=True)),
                ('email', models.EmailField(unique=True, max_length=255, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=False, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email_privacy', models.CharField(default=b'friends', max_length=50, choices=[(b'public', 'Public'), (b'friends', 'Friends'), (b'me', 'Only me')])),
                ('birthdate', models.DateField(null=True, blank=True)),
                ('birthdate_privacy', models.CharField(default=b'friends', max_length=50, choices=[(b'public', 'Public'), (b'friends', 'Friends'), (b'me', 'Only me')])),
                ('gender', models.CharField(max_length=50, null=True, choices=[(b'male', 'Male'), (b'female', 'Female')])),
                ('gender_privacy', models.CharField(default=b'friends', max_length=50, choices=[(b'public', 'Public'), (b'friends', 'Friends'), (b'me', 'Only me')])),
                ('country_privacy', models.CharField(default=b'friends', max_length=50, choices=[(b'public', 'Public'), (b'friends', 'Friends'), (b'me', 'Only me')])),
                ('city_privacy', models.CharField(default=b'friends', max_length=50, choices=[(b'public', 'Public'), (b'friends', 'Friends'), (b'me', 'Only me')])),
                ('address', models.CharField(max_length=255, null=True, blank=True)),
                ('address_privacy', models.CharField(default=b'friends', max_length=50, choices=[(b'public', 'Public'), (b'friends', 'Friends'), (b'me', 'Only me')])),
                ('postal_code', models.CharField(max_length=255, null=True, blank=True)),
                ('postal_code_privacy', models.CharField(default=b'friends', max_length=50, choices=[(b'public', 'Public'), (b'friends', 'Friends'), (b'me', 'Only me')])),
                ('city', models.ForeignKey(verbose_name='City', blank=True, to='cities_light.City', null=True)),
                ('country', models.ForeignKey(verbose_name='Country', blank=True, to='cities_light.Country', null=True)),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContactEmail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('privacy', models.CharField(default=b'friends', max_length=50, choices=[(b'public', 'Public'), (b'friends', 'Friends'), (b'me', 'Only me')])),
                ('email', models.EmailField(unique=True, max_length=255)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'accounts_user_contact_email',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContactPhone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('privacy', models.CharField(default=b'friends', max_length=50, choices=[(b'public', 'Public'), (b'friends', 'Friends'), (b'me', 'Only me')])),
                ('country_code', models.IntegerField(unique=True, max_length=255)),
                ('number', models.IntegerField(unique=True, max_length=255)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'accounts_user_contact_phone',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmailChangeRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=255)),
                ('hash_code', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('type', models.CharField(default=b'request', max_length=255)),
                ('status', models.CharField(default=b'pending', max_length=255)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'db_table': 'accounts_user_email_change_request',
                'get_latest_by': 'created_at',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PasswordResetRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hash_code', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(default=b'pending', max_length=255)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'db_table': 'accounts_user_password_reset_request',
                'get_latest_by': 'created_at',
            },
            bases=(models.Model,),
        ),
    ]
