from django.contrib.auth.tokens import PasswordResetTokenGenerator
from web.models import UserSettings

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        user_settings = UserSettings.objects.filter(user_id=user.pk).first()
        if not user_settings:
            raise Exception("Usersettings not found for "+user.username)

        return (
            str(user.pk) + str(timestamp) +
            str(user_settings.email_verified)
        )

account_activation_token = AccountActivationTokenGenerator()
