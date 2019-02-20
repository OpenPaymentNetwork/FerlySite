from sendgrid.helpers.mail import Content
from sendgrid.helpers.mail import Email
from sendgrid.helpers.mail import Mail
from twilio.rest import Client
import sendgrid


def send_email(request, to_email, subject, text,
               from_email='noreply@ferly.com'):
    sendgrid_api_key = request.ferlysettings.sendgrid_api_key
    if sendgrid_api_key is None:
        return 'no-credentials'
    sg = sendgrid.SendGridAPIClient(apikey=sendgrid_api_key)
    from_email = Email(from_email)
    to_email = Email(to_email)
    content = Content("text/plain", text)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
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
