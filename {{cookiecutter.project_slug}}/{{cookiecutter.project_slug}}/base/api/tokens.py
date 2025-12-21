from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import base36_to_int


class CustomPasswordResetTokenGenerator(PasswordResetTokenGenerator):
    token_checked = False

    def check_token(self, user, token):
        """
        Check if the token is valid for the given user.
        """
        self.token_checked = True
        return super().check_token(user, token)


    def is_token_expired(self,  token):
        """
        Check if the token is expired for the given user.
        """
        if not self.token_checked:
            msg = "Token must be checked before checking expiration."
            raise ValueError(msg)

        try:
            ts_b36, _ = token.split("-")
        except ValueError:
            return True
        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return True

        return self._num_seconds(self._now()) - ts > settings.PASSWORD_RESET_TIMEOUT


default_token_generator = CustomPasswordResetTokenGenerator()
