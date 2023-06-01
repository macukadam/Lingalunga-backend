from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
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


def send_reset_password_email(request, user, uid, token):
    verification_url = request.build_absolute_uri(
        reverse('password_reset_confirm', args=[uid, token]))

    subject = 'Password Reset'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email

    html_content = render_to_string('reset_password_email.html',
                                    {'username': user.username,
                                     'verification_url': verification_url})

    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


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


def google_get_or_create_user(backend, access_token, email):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        user = backend.do_auth(access_token)
    return user
