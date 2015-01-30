from django.conf.urls import url, include

urlpatterns = [
    # Login % Logout
    url(r'^signin/', 'accounts.views.signin', name="signin"),
    url(r'^signout/', 'accounts.views.signout', name="signout"),

    # Account: CRUD
    url(r'^signup/', 'accounts.views.create', name="signup"),
    url(r'^update/email', 'accounts.views.change_email', name="change_email"),
    url(r'^update/password', 'accounts.views.change_password', name="change_password"),
    url(r'^update/', 'accounts.views.update', name="update"),
    url(r'^deactivate/', 'accounts.views.deactivate', name="deactivate"),

    # Email confirmation
    url(r'^email/confirm/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/(?P<hash_code>[a-f0-9]{10})',
        'accounts.views.email_confirmation',
        name="email-confirmation"
    ),

    # Password reset
    url(r'^password/reset/', 'accounts.views.password_reset', name="password-reset"),
    url(r'^password/confirmation/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/(?P<hash_code>[a-f0-9]{10})',
        'accounts.views.password_reset_confirmation',
        name="password-reset-confirmation"
    ),

    # Ajax
    url(r'^ajax/cities/(?P<country_id>\d+)', 'accounts.views.cities', name="ajax_cities"),
]
