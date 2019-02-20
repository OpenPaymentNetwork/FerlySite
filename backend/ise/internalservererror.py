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
        except Exception as e:
            now = datetime.datetime.now()
            error_id = '{ts}|{uid}'.format(
                ts=now.strftime('%Y%m%d-%H%M%S'),
                uid=random.randint(100000, 999999))
            log.exception("Internal Server Error {0}".format(error_id))
            recipient = self.registry.settings.get('ise_recipient')
            if recipient:
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
                subject = '[Ferly ISE] {0}]'.format(error_id)
                send_email(request, recipient, subject, ise_text,
                           from_email='ise@ferly.com')
            response = Response(json="error:" + str(e))
            response.content_type = "text/plain"
            response.status_code = 500
            response.headers['Access-Control-Allow-Origin'] = '*'
        return response
