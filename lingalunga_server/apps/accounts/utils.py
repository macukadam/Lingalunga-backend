from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from lingalunga_server.apps.accounts.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


def send_verification_email(request, user, uid, token):
    verification_url = request.build_absolute_uri(
        reverse('verify-email', args=[uid, token]))
    subject = 'Email Verification'
    message = f'Please click the link to verify your email address: {verification_url}'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email
    send_mail(subject, message, from_email, [to_email], fail_silently=False)


def generate_email_verification_token(user: User):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uid, token


def authenticate(email=None, password=None):
    try:
        user = User.objects.get(email=email)
        if user.check_password(password):
            if user.is_active:
                return user
            else:
                raise Exception('User is not active.')
        else:
            raise Exception('Incorrect credentials.')

    except User.DoesNotExist as e:
        raise e
