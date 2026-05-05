If your email server is not configured properly, attempting to send an email will cause an Internal Server Error.

By default, ``django-allauth`` is setup to `have emails verifications mandatory`_,
which means it'll send a verification email when an unverified user tries to
log-in or when someone tries to sign-up.

Ensure your SMTP credentials are correct and that your mail server is accessible from your deployment environment.


.. _have emails verifications mandatory: https://docs.allauth.org/en/latest/account/configuration.html#email-verification
