from backend.communications import send_email
from backend.communications import send_sms
from unittest import TestCase
from unittest.mock import MagicMock


class TestSendEmail(TestCase):

    def _call(self, *args, **kw):
        return send_email(*args, **kw)

    def test_no_api_key(self):
        request = MagicMock()
        request.ferlysettings.sendgrid_api_key = None
        response = self._call(request, 'to@example.com', 'subject', 'text')
        self.assertEqual(response, 'no-credentials')


class TestSendSms(TestCase):

    def _call(self, *args, **kw):
        return send_sms(*args, **kw)

    def test_no_sid(self):
        request = MagicMock()
        request.ferlysettings.twilio_sid = None
        response = self._call(request, '+12025551234', 'text')
        self.assertEqual(response, 'no-credentials')

    def test_no_auth_token(self):
        request = MagicMock()
        request.ferlysettings.twilio_auth_token = None
        response = self._call(request, '+12025551234', 'text')
        self.assertEqual(response, 'no-credentials')

    def test_no_from(self):
        request = MagicMock()
        request.ferlysettings.twilio_from = None
        response = self._call(request, '+12025551234', 'text')
        self.assertEqual(response, 'no-credentials')
