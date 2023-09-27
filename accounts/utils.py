from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings

def detectUser(user):
    redirectUrl = ''
    if user.is_superadmin:
        redirectUrl = '/admin'
    elif user.is_admin:
        redirectUrl = 'adminDashboard'
    else:
        redirectUrl = 'guestDashboard'    
    return redirectUrl


def send_verification_email(request, user, mail_subject, email_template, password):
    from_email = settings.DEFAULT_FROM_EMAIL
    current_site = get_current_site(request)
    message = render_to_string(email_template, {
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
        'password': password
    })
    to_email = user.email
    mail = EmailMessage(mail_subject, message, from_email, to=[to_email])
    mail.send()


