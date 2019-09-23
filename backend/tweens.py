from pyramid.response import Response
from six import StringIO
import datetime
import logging
import traceback

log = logging.getLogger(__name__)


class HeaderTween(object):
    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

    def __call__(self, request):
        response = self.handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = "Authorization, Content-Type"
        return response
