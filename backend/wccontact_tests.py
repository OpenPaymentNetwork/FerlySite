from backend.wccontact import wc_contact
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch
import pyramid.testing


class TestWCContact(TestCase):

    def _call(self, *args, **kw):
        return wc_contact(*args, **kw)

    @patch('requests.get')
    @patch('requests.post')
    def test_get(self, mock_post, mock_get):
        request = pyramid.testing.DummyRequest()
        mock_settings = request.ferlysettings = MagicMock()
        mock_settings.wingcash_api_url = 'url'
        self._call(request, 'GET', 'urlTail', access_token='token')
        self.assertFalse(mock_post.called)
        self.assertTrue(mock_get.called)

    @patch('requests.get')
    @patch('requests.post')
    def test_post(self, mock_post, mock_get):
        request = pyramid.testing.DummyRequest()
        mock_settings = request.ferlysettings = MagicMock()
        mock_settings.wingcash_api_url = 'url'
        self._call(request, 'POST', 'urlTail', access_token='token')
        self.assertFalse(mock_get.called)
        self.assertTrue(mock_post.called)

    @patch('requests.get')
    @patch('requests.post')
    def test_invalid_method(self, mock_get, mock_post):
        request = pyramid.testing.DummyRequest()
        with self.assertRaises(Exception) as cm:
            self._call(request, 'PUT', 'urlTail', access_token='token')
        expected_error = "Only 'GET' and 'POST' are accepted methods"
        self.assertEqual(expected_error, str(cm.exception))

    @patch('requests.get')
    def test_auth(self, mock_get):
        request = pyramid.testing.DummyRequest()
        mock_settings = request.ferlysettings = MagicMock()
        mock_settings.wingcash_api_url = 'url'
        mock_settings.wingcash_client_id = 'client_id'
        mock_settings.wingcash_client_secret = 'client_secret'
        self._call(request, 'GET', 'urlTail', access_token='token', auth=True)
        auth = ('client_id', 'client_secret')
        kw = {'auth': auth, 'params': {}}
        mock_get.assert_called_once_with('url/urlTail', **kw)

    @patch('requests.get')
    def test_headers(self, mock_get):
        request = pyramid.testing.DummyRequest()
        mock_settings = request.ferlysettings = MagicMock()
        mock_settings.wingcash_api_url = 'url'
        access_token = 'token'
        self._call(request, 'GET', 'urlTail', access_token=access_token)
        header = {'headers': {'Authorization': 'Bearer ' + access_token}}
        mock_get.assert_called_once_with('url/urlTail', **header, params={})

    @patch('requests.get')
    def test_settings_token(self, mock_get):
        request = pyramid.testing.DummyRequest()
        mock_settings = request.ferlysettings = MagicMock()
        mock_settings.wingcash_api_url = 'url'
        access_token = 'token'
        mock_settings.wingcash_api_token = access_token
        self._call(request, 'GET', 'urlTail')
        header = {'headers': {'Authorization': 'Bearer ' + access_token}}
        mock_get.assert_called_once_with('url/urlTail', **header, params={})

    @patch('requests.get')
    def test_token_priority(self, mock_get):
        request = pyramid.testing.DummyRequest()
        mock_settings = request.ferlysettings = MagicMock()
        mock_settings.wingcash_api_url = 'url'
        access_token = 'token'
        mock_settings.wingcash_api_token = 'wrong_token'
        self._call(request, 'GET', 'urlTail', access_token=access_token)
        header = {'headers': {'Authorization': 'Bearer ' + access_token}}
        mock_get.assert_called_once_with('url/urlTail', **header, params={})

    @patch('requests.get')
    def test_params(self, mock_get):
        request = pyramid.testing.DummyRequest()
        mock_settings = request.ferlysettings = MagicMock()
        mock_settings.wingcash_api_url = 'url'
        access_token = 'token'
        params = {'key': 'value'}
        self._call(request, 'GET', 'urlTail', access_token=access_token,
                   params=params)
        header = {'headers': {'Authorization': 'Bearer ' + access_token}}
        mock_get.assert_called_once_with('url/urlTail', **header,
                                         params=params)

    @patch('requests.get')
    def test_url_tail(self, mock_get):
        request = pyramid.testing.DummyRequest()
        mock_settings = request.ferlysettings = MagicMock()
        mock_settings.wingcash_api_url = 'https://www.example.com/'
        expected_url = 'https://www.example.com/urlTail'
        self._call(request, 'GET', '/urlTail', access_token='token')
        self.assertEqual(mock_get.call_args[0][0], expected_url)
        self._call(request, 'GET', 'urlTail', access_token='token')
        self.assertEqual(mock_get.call_args[0][0], expected_url)
        self._call(request, 'GET', '/url/Tail/', access_token='token')
        expected_url = 'https://www.example.com/url/Tail'
        self.assertEqual(mock_get.call_args[0][0], expected_url)

    @patch('requests.post')
    def test_data(self, mock_post):
        request = pyramid.testing.DummyRequest()
        mock_settings = request.ferlysettings = MagicMock()
        mock_settings.wingcash_api_url = 'url'
        access_token = 'token'
        data = {'key': 'value'}
        self._call(request, 'POST', 'urlTail', access_token=access_token,
                   params=data)
        header = {'headers': {'Authorization': 'Bearer ' + access_token}}
        mock_post.assert_called_once_with('url/urlTail', **header,
                                          data=data)

    @patch('requests.get')
    def test_raise_for_status_called(self, get):
        request = pyramid.testing.DummyRequest()
        mock_settings = request.ferlysettings = MagicMock()
        mock_settings.wingcash_api_url = 'url'
        wc_response = get.return_value
        self._call(request, 'GET', 'urlTail')
        self.assertTrue(wc_response.raise_for_status.called)
