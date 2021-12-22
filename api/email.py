from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode
from templated_mail.mail import BaseEmailMessage
from django.conf import settings

def encode_uid(pk):
    return force_str(urlsafe_base64_encode(force_bytes(pk)))

class PasswordResetEmail(BaseEmailMessage):
    """Email for sending if requested password reset by user"""
    template_name = "email/password_reset.html"

    def get_context_data(self):
        context = super().get_context_data()

        user = context.get("user")
        context["uid"] = encode_uid(user.pk)
        context["token"] = default_token_generator.make_token(user)
        context["url"] = settings.DJOSER["PASSWORD_RESET_CONFIRM_URL"].format(**context)
        return context


class AwardSuccessVerified(BaseEmailMessage):
    """Email for sending to user if him award 
    is successfully verified by administation"""
    template_name = "email/award/accept.html"


class AwardNoVerified(BaseEmailMessage):
    """Email for sending to user if him award 
    is not verified by administation"""
    template_name = "email/award/noaccept.html"
