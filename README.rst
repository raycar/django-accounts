=====
django-accounts
=====

Simple django app to controll user's accounts.

Detailed documentation can be found in the "docs" directory.

Quick start
-----------

1. Add "django-accounts" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'django-accounts',
    )

2. Include the polls URLconf in your project urls.py like this::

    url(r'^accounts/', include('django-accounts.urls')),

3. Run `python manage.py migrate` to create the django-accounts models.

4. Start the development server and visit http://127.0.0.1:8000/accounts/create
        to create an account.
