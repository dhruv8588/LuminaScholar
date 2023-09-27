from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from LuminaScholar import settings


def send_review_invitation_email(request, reviewer, paper_id):
    mail_template = 'accounts/emails/review_invitation.html'
    from_email = settings.DEFAULT_FROM_EMAIL
    mail_subject = 'Invitation to Review'
    to_email = reviewer.email

    current_site = get_current_site(request)
    message = render_to_string(mail_template, {
        'reviewer': reviewer,
        'paper_id': paper_id,
        'domain': current_site,
    })
    
    mail = EmailMessage(mail_subject, message, from_email, to=[to_email])
    mail.send()

    
