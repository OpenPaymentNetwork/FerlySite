from backend.database import (
    get_engine,
    get_session_factory,
    get_tm_session,
)
from backend.database.meta import Base
from backend.database.models import CardRequest
from backend.database.models import now_utc
from pyramid.paster import bootstrap
from pyramid.paster import get_appsettings
from sendgrid.helpers.mail import Attachment
from sendgrid.helpers.mail import Content
from sendgrid.helpers.mail import Email
from sendgrid.helpers.mail import Mail
import base64
import csv
import os
import sendgrid
import sys
import transaction


# run as env/bin/python3 <email_pending_card_requests.py> <staging.ini>
if __name__ == '__main__':
    config_uri = sys.argv[1]
    settings = get_appsettings(config_uri)

    engine = get_engine(settings)
    Base.metadata.create_all(engine)
    session_factory = get_session_factory(engine)

    sendgrid_api_key = bootstrap(
        config_uri)['request'].ferlysettings.sendgrid_api_key

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)
        addresses = dbsession.query(CardRequest).filter(
            CardRequest.downloaded.is_(None)).all()

        if len(addresses) > 0:
            file_title = 'Card Fulfillment.csv'
            with open(file_title, 'w') as csvfile:
                filewriter = csv.writer(csvfile)
                for address in addresses:
                    filewriter.writerow([
                        address.name,
                        address.line1,
                        address.line2,
                        address.city,
                        address.state,
                        address.zip_code
                    ])
                    address.downloaded = now_utc

            with open(file_title, 'rb') as fd:
                data = base64.b64encode(fd.read())
            sg = sendgrid.SendGridAPIClient(apikey=sendgrid_api_key)
            attachment = Attachment()
            attachment.content = str(data, 'utf-8')
            attachment.filename = file_title
            content = Content("text/plain", f"{len(addresses)} more requests.")
            from_email = Email('no-reply@ferly.com')
            to_email = Email('brad@ferly.com')
            mail = Mail(from_email, 'Card Fulfillment', to_email, content)
            mail.add_attachment(attachment)
            response = sg.client.mail.send.post(request_body=mail.get())

            os.remove(file_title)
