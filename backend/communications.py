from sendgrid.helpers.mail import Mail
from twilio.rest import Client
import sendgrid


def send_email(request, to_email, subject, text,
               from_email='no-reply@ferly.com'):
    sendgrid_api_key = request.ferlysettings.sendgrid_api_key
    if sendgrid_api_key is None:
        return 'no-credentials'
    sg = sendgrid.SendGridAPIClient(sendgrid_api_key)
    mail = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        plain_text_content=text)
    response = sg.send(mail)
    return response.status_code


def send_sms(request, to_number, text):
    twilio_sid = request.ferlysettings.twilio_sid
    twilio_auth_token = request.ferlysettings.twilio_auth_token
    from_ = request.ferlysettings.twilio_from
    if None in (twilio_sid, twilio_auth_token, from_):
        return 'no-credentials'
    client = Client(twilio_sid, twilio_auth_token)
    response = client.messages.create(body=text, from_=from_, to=to_number)
    return response.status
