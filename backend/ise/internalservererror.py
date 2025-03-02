from backend.communications import send_email
from pyramid.response import Response
from six import StringIO
import datetime
import logging
import random
import traceback

log = logging.getLogger(__name__)


class InternalServerErrorTween(object):
    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

    def __call__(self, request):
        try:
            response = self.handler(request)
        except Exception:
            now = datetime.datetime.utcnow()
            error_id = '{ts}-{uid}'.format(
                ts=now.strftime('%Y%m%d-%H%M%S'),
                uid=random.randint(100000, 999999))
            log.exception("Internal Server Error {0}".format(error_id))
            recipients = self.registry.settings.get('ise_recipients')
            if recipients:
                recipients = recipients.split(', ')
                traceback_file = StringIO()
                traceback.print_exc(file=traceback_file)
                lines = []
                lines.append('Date: {0}'.format(now.isoformat()))
                lines.append('')
                lines.append(
                    'Path: {0}'.format(request.environ.get('PATH_INFO')))
                lines.append('')
                lines.append(traceback_file.getvalue().strip())
                ise_text = '\n'.join(lines)
                request._ise_text = ise_text
                subject = '[ferlyapi.com ISE] {0}]'.format(error_id)
                for recipient in recipients:
                    send_email(request, recipient, subject, ise_text,
                            from_email='ise@ferly.com')
            response = Response(json={
                'error': 'internal_server_error:%s' % error_id,
                'error_description': (
                    "Sorry, an internal server error occurred. "
                    "Error ID: %s. Ferly staff will be notified." % error_id),
                })
            response.content_type = "application/json"
            response.status_code = 500
            response.headers['Access-Control-Allow-Origin'] = '*'
        return response
