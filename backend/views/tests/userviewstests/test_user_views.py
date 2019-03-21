from backend import schema
from backend.models.models import Design
from backend.models.models import Device
from backend.models.models import User
from backend.views.userviews.userviews import edit_profile
from backend.views.userviews.userviews import history
from backend.views.userviews.userviews import is_user
from backend.views.userviews.userviews import signup
from backend.views.userviews.userviews import transfer
from unittest import TestCase
from unittest.mock import call
from unittest.mock import MagicMock
from unittest.mock import patch
import pyramid.testing


class TestSignUp(TestCase):

    def _call(self, *args, **kw):
        return signup(*args, **kw)

    def _make_request(self, **kw):
        request_params = {
            'device_id': 'defaultdeviceid',
            'first_name': 'defaultfirstname',
            'last_name': 'defaultlastname',
            'username': 'defaultusername',
            'expo_token:': 'defaulttoken',
            'os': 'defaultos:android'
        }
        request_params.update(**kw)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = MagicMock()
        request.get_params = params = MagicMock()
        params.return_value = schema.RegisterSchema().bind(
            request=request).deserialize(request_params)
        return request

    def test_correct_schema_used(self):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schema.RegisterSchema))

    def test_already_registered(self):
        request = self._make_request()
        mock_query = request.dbsession.query.return_value
        mdevice = MagicMock()
        mock_query.filter.return_value.first.return_value = mdevice
        response = self._call(request)
        expected_response = {'error': 'device_already_registered'}
        self.assertEqual(response, expected_response)

    def test_query(self):
        device_id = '123'
        request = self._make_request(device_id=device_id)
        mock_query = request.dbsession.query = MagicMock()
        mock_filter = mock_query.return_value.filter = MagicMock()
        self._call(request)
        expression = Device.device_id == device_id
        self.assertTrue(expression.compare(mock_filter.call_args[0][0]))

    @patch('backend.views.userviews.userviews.Device')
    @patch('backend.views.userviews.userviews.User')
    @patch('backend.views.userviews.userviews.wc_contact')
    def test_add_user(self, mock_wc_contact, mock_user, mock_device):
        first_name = 'firstname'
        last_name = 'lastname'
        username = 'username'
        request = self._make_request(
            first_name=first_name, last_name=last_name, username=username)
        mock_query = request.dbsession.query.return_value
        mock_query.filter.return_value.first.return_value = None
        wc_id = 'newid'
        mock_wc_contact.return_value.json.return_value = {'id': wc_id}
        mock_user.return_value.id = 'userid'
        user = {'wc_id': wc_id, 'first_name': first_name, 'username': username,
                'last_name': last_name}
        self._call(request)
        mock_user.assert_called_once_with(**user)
        request.dbsession.add.assert_any_call(mock_user.return_value)

    @patch('backend.views.userviews.userviews.Device')
    @patch('backend.views.userviews.userviews.User')
    @patch('backend.views.userviews.userviews.wc_contact')
    def test_add_device(self, mock_wc_contact, mock_user, mock_device):
        device_id = 'deviceid'
        os = 'android:28'
        expo_token = 'myexpotoken'
        request = self._make_request(
            device_id=device_id, os=os, expo_token=expo_token)
        mock_query = request.dbsession.query.return_value
        mock_query.filter.return_value.first.return_value = None
        mock_user.return_value.id = user_id = 'userid'
        device = {'device_id': device_id, 'user_id': user_id, 'os': os,
                  'expo_token': expo_token}
        self._call(request)
        mock_device.assert_called_once_with(**device)
        request.dbsession.add.assert_any_call(mock_device.return_value)

    @patch('backend.views.userviews.userviews.Device')
    @patch('backend.views.userviews.userviews.User')
    @patch('backend.views.userviews.userviews.wc_contact')
    def test_db_flush(self, mock_wc_contact, mock_user, mock_device):
        request = self._make_request()
        mock_query = request.dbsession.query.return_value
        mock_query.filter.return_value.first.return_value = None
        mdevice = mock_device.return_value
        muser = mock_user.return_value
        self._call(request)
        request.dbsession.assert_has_calls(
            [call.add(muser), call.flush, call.add(mdevice)])

    @patch('backend.views.userviews.userviews.Device')
    @patch('backend.views.userviews.userviews.User')
    @patch('backend.views.userviews.userviews.wc_contact')
    def test_update_tsvector(self, mock_wc_contact, mock_user, mock_device):
        request = self._make_request()
        mock_query = request.dbsession.query.return_value
        mock_query.filter.return_value.first.return_value = None
        muser = mock_user.return_value
        self._call(request)
        muser.update_tsvector.assert_called()

    @patch('backend.views.userviews.userviews.wc_contact')
    def test_wc_contact_params(self, mock_wc_contact):
        first_name = 'firstname'
        last_name = 'lastname'
        request = self._make_request(
            first_name=first_name, last_name=last_name)
        mock_query = request.dbsession.query.return_value
        mock_query.filter.return_value.first.return_value = None
        self._call(request)
        args = (request, 'POST', 'p/add-individual')
        params = {
            'first_name': first_name,
            'last_name': last_name,
            'agreed_terms_and_privacy': True
        }
        kw = {
            'params': params,
            'auth': True
        }
        mock_wc_contact.assert_called_once_with(*args, **kw)

    def test_deny_existing_username(self):
        request = self._make_request()
        mock_filter = request.dbsession.query.return_value.filter.return_value
        mock_filter.first.side_effect = [None, not None]
        response = self._call(request)
        self.assertEqual(response, {'error': 'existing_username'})


class TestEditProfile(TestCase):

    def _call(self, *args, **kw):
        return edit_profile(*args, **kw)

    def _make_request(self, **kw):
        request_params = {
            'device_id': 'defaultdeviceid',
            'first_name': 'defaultfirstname',
            'last_name': 'defaultlastname',
            'username': 'defaultusername'
        }
        request_params.update(**kw)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = MagicMock()
        request.get_params = params = MagicMock()
        params.return_value = schema.EditProfileSchema().bind(
            request=request).deserialize(request_params)
        return request

    def test_correct_schema_used(self):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schema.EditProfileSchema))

    @patch('backend.views.userviews.userviews.wc_contact')
    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.get_device')
    def test_unchanged_username(self, get_device, get_token, wc_contact):
        request = self._make_request()
        mock_user = get_device.return_value.user
        mock_filter = request.dbsession.query.return_value.filter.return_value
        mock_filter.first.return_value = mock_user
        response = self._call(request)
        self.assertEqual(response, {})

    @patch('backend.views.userviews.userviews.get_device')
    def test_existing_username(self, get_device):
        request = self._make_request()
        mock_filter = request.dbsession.query.return_value.filter.return_value
        mock_filter.first.return_value = not None
        response = self._call(request)
        self.assertEqual(response, {'error': 'existing_username'})

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    @patch('backend.views.userviews.userviews.get_device')
    def test_edit_username_only(self, get_device, wc_contact, get_wc_token):
        mock_user = get_device.return_value.user
        mock_user.first_name = current_first_name = 'firstname'
        mock_user.last_name = current_last_name = 'lastname'
        mock_user.username = 'current_username'
        newusername = 'newusername'
        request = self._make_request(
            first_name=current_first_name,
            last_name=current_last_name,
            username=newusername
        )
        mock_filter = request.dbsession.query.return_value.filter.return_value
        mock_filter.first.return_value = None
        self._call(request)
        self.assertFalse(get_wc_token.called)
        self.assertFalse(wc_contact.called)
        self.assertEqual(mock_user.first_name, current_first_name)
        self.assertEqual(mock_user.last_name, current_last_name)
        self.assertEqual(mock_user.username, newusername)

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    @patch('backend.views.userviews.userviews.get_device')
    def test_edit_first_name_only(self, get_device, wc_contact, get_wc_token):
        mock_user = get_device.return_value.user
        mock_user.first_name = 'firstname'
        mock_user.last_name = current_last_name = 'lastname'
        mock_user.username = current_username = 'username'
        new_first_name = 'new_first_name'
        request = self._make_request(
            first_name=new_first_name,
            last_name=current_last_name,
            username=current_username
        )
        mock_filter = request.dbsession.query.return_value.filter.return_value
        mock_filter.first.return_value = None
        self._call(request)
        get_wc_token.assert_called_with(request, mock_user)
        wc_contact.assert_called_with(
            request,
            'POST',
            'wallet/change-name',
            access_token=get_wc_token.return_value,
            params={
                'first_name': new_first_name,
                'last_name': current_last_name
            })
        self.assertEqual(mock_user.first_name, new_first_name)
        self.assertEqual(mock_user.last_name, current_last_name)
        self.assertEqual(mock_user.username, current_username)

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    @patch('backend.views.userviews.userviews.get_device')
    def test_edit_last_name_only(self, get_device, wc_contact, get_wc_token):
        mock_user = get_device.return_value.user
        mock_user.first_name = current_first_name = 'firstname'
        mock_user.last_name = 'lastname'
        mock_user.username = current_username = 'username'
        new_last_name = 'new_first_name'
        request = self._make_request(
            first_name=current_first_name,
            last_name=new_last_name,
            username=current_username
        )
        mock_filter = request.dbsession.query.return_value.filter.return_value
        mock_filter.first.return_value = None
        self._call(request)
        get_wc_token.assert_called_with(request, mock_user)
        wc_contact.assert_called_with(
            request,
            'POST',
            'wallet/change-name',
            access_token=get_wc_token.return_value,
            params={
                'first_name': current_first_name,
                'last_name': new_last_name
            })
        self.assertEqual(mock_user.first_name, current_first_name)
        self.assertEqual(mock_user.last_name, new_last_name)
        self.assertEqual(mock_user.username, current_username)

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    @patch('backend.views.userviews.userviews.get_device')
    def test_update_tsvector(self, get_device, wc_contact, get_wc_token):
        mock_user = get_device.return_value.user
        request = self._make_request()
        mock_filter = request.dbsession.query.return_value.filter.return_value
        mock_filter.first.return_value = None
        self._call(request)
        mock_user.update_tsvector.assert_called()


class TestIsUser(TestCase):

    def _call(self, *args, **kw):
        return is_user(*args, **kw)

    def _make_request(self, **args):
        request_params = {'device_id': args.get('device_id', 'defaultdevice')}
        if args.get('expected_env'):
            request_params.update({'expected_env', args['expected_env']})
        request = pyramid.testing.DummyRequest(params=request_params)
        settings = request.ferlysettings = MagicMock()
        settings.environment = args.get('environment', 'staging')
        request.dbsession = MagicMock()
        request.get_params = params = MagicMock()
        params.return_value = schema.IsUserSchema().bind(
            request=request).deserialize(request_params)
        return request

    def test_correct_schema_used(self):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schema.IsUserSchema))

    def test_expected_env_mismatch(self):
        response = self._call(self._make_request(environment='production'))
        self.assertEqual(response, {'error': 'unexpected_environment'})

    def test_invalid_device_id(self):
        request = self._make_request()
        mock_query = request.dbsession.query.return_value
        mock_query.filter.return_value.first.return_value = None
        response = self._call(request)
        self.assertFalse(response.get('is_user'))

    def test_valid_device_id(self):
        response = self._call(self._make_request())
        self.assertTrue(response.get('is_user'))

    def test_query(self):
        device_id = '123'
        request = self._make_request(device_id=device_id)
        mock_filter = request.dbsession.query.return_value.filter
        self._call(request)
        expression = Device.device_id == device_id
        self.assertTrue(expression.compare(mock_filter.call_args[0][0]))


class TestHistory(TestCase):

    def _call(self, *args, **kw):
        return history(*args, **kw)

    def _make_request(self, **kw):
        request_params = {
            'device_id': 'defaultdeviceid'
        }
        request_params.update(**kw)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = MagicMock()
        request.get_params = params = MagicMock()
        params.return_value = schema.HistorySchema().bind(
            request=request).deserialize(request_params)
        return request

    def _make_transfer(self, **kw):
        loop_id = kw.pop('loop_id', 'defaultloopid')
        sender_title = kw.pop('sender_title', 'defaultsendertitle')
        sender_is_individual = kw.pop('sender_is_individual', True)
        recipient_title = kw.pop('recipient_title', 'defaultrecipienttitle')
        recipient_is_individual = kw.pop('recipient_is_individual', True)
        transfer = {
            'amount': 0,
            'timestamp': 'timestamp',
            'movements': [{'loops': [{'loop_id': loop_id}]}],
            'sender_info': {
                'title': sender_title, 'is_individual': sender_is_individual},
            'recipient_info': {
                'title': recipient_title,
                'is_individual': recipient_is_individual
            },
            'recipient_id': 'defaultrecipientid',
            'sender_id': 'defaultsenderid',
            'id': 'defaultid'
        }
        transfer.update(**kw)
        return transfer

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    def test_correct_schema_used(self, wc_contact, get_wc_token):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schema.HistorySchema))

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    @patch('backend.views.userviews.userviews.get_device')
    def test_get_wc_contact_args(self, get_device, wc_contact, get_wc_token):
        limit = 100
        offset = 0
        user = get_device.return_value.user
        access_token = get_wc_token.return_value
        request = self._make_request(limit=limit, offset=offset)
        post_params = {'limit': limit, 'offset': offset}
        self._call(request)
        get_device.assert_called()
        get_wc_token.assert_called_with(request, user)
        wc_contact.assert_called_with(
            request, 'GET', 'wallet/history', params=post_params,
            access_token=access_token)

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    def test_has_more_is_returned(self, wc_contact, get_wc_token):
        more = True
        wc_contact.return_value.json.return_value = {'more': more}
        response = self._call(self._make_request())
        self.assertEqual(more, response['has_more'])

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    def test_design_query(self, wc_contact, get_wc_token):
        loop_id = 'myloop_id'
        results = [self._make_transfer(loop_id=loop_id)]
        wc_contact.return_value.json.return_value = {'results': results}
        request = self._make_request()
        mock_filter = request.dbsession.query.return_value.filter
        self._call(request)
        expression = Design.wc_id == loop_id
        self.assertTrue(expression.compare(mock_filter.call_args[0][0]))

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    def test_design_title_is_returned(self, wc_contact, get_wc_token):
        request = self._make_request()
        results = [self._make_transfer()]
        wc_contact.return_value.json.return_value = {'results': results}
        mock_filter = request.dbsession.query.return_value.filter
        mock_design = mock_filter.return_value.first.return_value
        mock_design.title = 'ftitle'
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['design_title'], 'ftitle')

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    def test_design_image_url_is_returned(self, wc_contact, get_wc_token):
        request = self._make_request()
        results = [self._make_transfer()]
        wc_contact.return_value.json.return_value = {'results': results}
        mock_filter = request.dbsession.query.return_value.filter
        mock_design = mock_filter.return_value.first.return_value
        mock_design.image_url = 'fimage_url'
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['design_image_url'], 'fimage_url')

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    def test_amount_is_returned(self, wc_contact, get_wc_token):
        amount = 10
        request = self._make_request()
        results = [self._make_transfer(amount=amount)]
        wc_contact.return_value.json.return_value = {'results': results}
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['amount'], amount)

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    def test_timestamp_is_returned(self, wc_contact, get_wc_token):
        import datetime
        timestamp = datetime.datetime.utcnow()
        request = self._make_request()
        results = [self._make_transfer(timestamp=timestamp)]
        wc_contact.return_value.json.return_value = {'results': results}
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['timestamp'], timestamp)

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    def test_id_is_returned(self, wc_contact, get_wc_token):
        transfer_id = 'mytransfer_id'
        request = self._make_request()
        results = [self._make_transfer(id=transfer_id)]
        wc_contact.return_value.json.return_value = {'results': results}
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['id'], transfer_id)

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    def test_multiple_results(self, wc_contact, get_wc_token):
        request = self._make_request()
        transfer = self._make_transfer()
        results = [transfer, transfer, transfer]
        wc_contact.return_value.json.return_value = {'results': results}
        response = self._call(request)
        self.assertEqual(len(response['history']), len(results))

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    @patch('backend.views.userviews.userviews.get_device')
    def test_sender_counter_party(self, get_device, wc_contact, get_wc_token):
        user_wc_id = 'myuserid'
        recipient_title = 'myrecipient_title'
        request = self._make_request()
        results = [self._make_transfer(
            sender_id=user_wc_id, recipient_title=recipient_title)]
        wc_contact.return_value.json.return_value = {'results': results}
        user = get_device.return_value.user
        user.wc_id = user_wc_id
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['counter_party'], recipient_title)

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    @patch('backend.views.userviews.userviews.get_device')
    def test_recipient_counter_party(
            self, get_device, wc_contact, get_wc_token):
        recipient_wc_id = 'myuserid'
        sender_title = 'mysender_title'
        request = self._make_request()
        results = [self._make_transfer(
            recipient_id=recipient_wc_id, sender_title=sender_title)]
        wc_contact.return_value.json.return_value = {'results': results}
        user = get_device.return_value.user
        user.wc_id = recipient_wc_id
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['counter_party'], sender_title)

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    @patch('backend.views.userviews.userviews.get_device')
    def test_redeem_type(self, get_device, wc_contact, get_wc_token):
        sender_wc_id = 'mywcid'
        request = self._make_request()
        results = [self._make_transfer(
            sender_id=sender_wc_id, recipient_is_individual=False)]
        wc_contact.return_value.json.return_value = {'results': results}
        user = get_device.return_value.user
        user.wc_id = sender_wc_id
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['transfer_type'], 'redeem')

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    @patch('backend.views.userviews.userviews.get_device')
    def test_send_type(self, get_device, wc_contact, get_wc_token):
        sender_wc_id = 'mywcid'
        request = self._make_request()
        results = [self._make_transfer(
            sender_id=sender_wc_id, recipient_is_individual=True)]
        wc_contact.return_value.json.return_value = {'results': results}
        user = get_device.return_value.user
        user.wc_id = sender_wc_id
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['transfer_type'], 'send')

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    @patch('backend.views.userviews.userviews.get_device')
    def test_receive_type(self, get_device, wc_contact, get_wc_token):
        recipient_wc_id = 'mywcid'
        request = self._make_request()
        results = [self._make_transfer(
            recipient_id=recipient_wc_id, sender_is_individual=True)]
        wc_contact.return_value.json.return_value = {'results': results}
        user = get_device.return_value.user
        user.wc_id = recipient_wc_id
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['transfer_type'], 'receive')

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    @patch('backend.views.userviews.userviews.get_device')
    def test_purchase_type(self, get_device, wc_contact, get_wc_token):
        recipient_wc_id = 'mywcid'
        request = self._make_request()
        results = [self._make_transfer(
            recipient_id=recipient_wc_id, sender_is_individual=False)]
        wc_contact.return_value.json.return_value = {'results': results}
        user = get_device.return_value.user
        user.wc_id = recipient_wc_id
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['transfer_type'], 'purchase')

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    @patch('backend.views.userviews.userviews.get_device')
    def test_unrecognized_design(self, get_device, wc_contact, get_wc_token):
        request = self._make_request()
        results = [self._make_transfer()]
        wc_contact.return_value.json.return_value = {'results': results}
        mock_filter = request.dbsession.query.return_value.filter
        mock_filter.return_value.first.return_value = None
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['design_title'], 'Unrecognized')
        self.assertEqual(transfer['design_image_url'], '')

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    @patch('backend.views.userviews.userviews.get_device')
    def test_unrecognized_user_role(
            self, get_device, wc_contact, get_wc_token):
        request = self._make_request()
        results = [self._make_transfer()]
        wc_contact.return_value.json.return_value = {'results': results}
        mock_filter = request.dbsession.query.return_value.filter
        mock_filter.return_value.first.return_value = None
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['transfer_type'], 'unrecognized')


class TestTransfer(TestCase):

    def _call(self, *args, **kw):
        return transfer(*args, **kw)

    def _make_request(self, **kw):
        request_params = {
            'device_id': 'defaultdeviceid',
            'transfer_id': 'defaulttransferid'
        }
        request_params.update(**kw)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = MagicMock()
        request.get_params = params = MagicMock()
        params.return_value = schema.TransferSchema().bind(
            request=request).deserialize(request_params)
        return request

    def _make_transfer(self, **kw):
        sender_id = kw.pop('sender_id', 'defaultsenderid')
        recipient_id = kw.pop('recipient_id', 'defaultrecipientid')
        sender_is_individual = kw.pop('sender_is_individual', True)
        recipient_is_individual = kw.pop('recipient_is_individual', True)
        transfer = {
            'sender_info': {
                'uid_value': sender_id,
                'is_individual': sender_is_individual
            },
            'recipient_info': {
                'uid_value': recipient_id,
                'is_individual': recipient_is_individual
            },
            'recipient_id': recipient_id,
            'sender_id': sender_id,
            'message': 'defaultmessage'
        }
        transfer.update(**kw)
        return transfer

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    def test_correct_schema_used(self, wc_contact, get_wc_token):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schema.TransferSchema))

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    @patch('backend.views.userviews.userviews.get_device')
    def test_get_wc_contact_args(self, get_device, wc_contact, get_wc_token):
        transfer_id = 'mytransferid'
        user = get_device.return_value.user
        access_token = get_wc_token.return_value
        request = self._make_request(transfer_id=transfer_id)
        self._call(request)
        get_device.assert_called()
        get_wc_token.assert_called_with(request, user)
        wc_contact.assert_called_with(
            request, 'GET', 't/{0}'.format(transfer_id),
            access_token=access_token)

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    @patch('backend.views.userviews.userviews.get_device')
    def test_message_is_returned(self, get_device, wc_contact, get_wc_token):
        message = 'mymessage'
        user_id = 'myuserid'
        user = get_device.return_value.user
        user.wc_id = user_id
        transfer = self._make_transfer(sender_id=user_id, message=message)
        wc_contact.return_value.json.return_value = transfer
        response = self._call(self._make_request())
        self.assertEqual(response['message'], message)

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    @patch('backend.views.userviews.userviews.get_device')
    def test_sender_counter_party(self, get_device, wc_contact, get_wc_token):
        recipient_id = 'myrecipientid'
        sender_id = 'mysenderid'
        user = get_device.return_value.user
        user.wc_id = recipient_id
        transfer = self._make_transfer(
            recipient_id=recipient_id, sender_id=sender_id)
        wc_contact.return_value.json.return_value = transfer
        request = self._make_request()
        mock_filter = request.dbsession.query.return_value.filter
        self._call(request)
        expression = User.wc_id == sender_id
        self.assertTrue(expression.compare(mock_filter.call_args[0][0]))

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    @patch('backend.views.userviews.userviews.get_device')
    def test_recipient_counter_party(
            self, get_device, wc_contact, get_wc_token):
        sender_id = 'mysenderid'
        recipient_id = 'myrecipientid'
        user = get_device.return_value.user
        user.wc_id = sender_id
        transfer = self._make_transfer(
            recipient_id=recipient_id, sender_id=sender_id)
        wc_contact.return_value.json.return_value = transfer
        request = self._make_request()
        mock_filter = request.dbsession.query.return_value.filter
        self._call(request)
        expression = User.wc_id == recipient_id
        self.assertTrue(expression.compare(mock_filter.call_args[0][0]))

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    @patch('backend.views.userviews.userviews.get_device')
    def test_permission_denied(self, get_device, wc_contact, get_wc_token):
        recipient_id = 'myrecipientid'
        sender_id = 'mysenderid'
        user = get_device.return_value.user
        user.wc_id = 'differentid'
        transfer = self._make_transfer(
            recipient_id=recipient_id, sender_id=sender_id)
        wc_contact.return_value.json.return_value = transfer
        response = self._call(self._make_request())
        self.assertEqual(response, {'error': 'permission_denied'})

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    @patch('backend.views.userviews.userviews.get_device')
    def test_query_for_users_only(self, get_device, wc_contact, get_wc_token):
        sender_id = 'mysenderid'
        user = get_device.return_value.user
        user.wc_id = sender_id
        transfer = self._make_transfer(
            sender_id=sender_id, recipient_is_individual=False)
        wc_contact.return_value.json.return_value = transfer
        request = self._make_request()
        self._call(request)
        request.dbsession.query.assert_not_called()

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    @patch('backend.views.userviews.userviews.get_device')
    def test_no_counter_party_user(self, get_device, wc_contact, get_wc_token):
        sender_id = 'mysenderid'
        user = get_device.return_value.user
        user.wc_id = sender_id
        transfer = self._make_transfer(sender_id=sender_id)
        wc_contact.return_value.json.return_value = transfer
        request = self._make_request()
        mock_filter = request.dbsession.query.return_value.filter.return_value
        mock_filter.first.return_value = None
        response = self._call(request)
        self.assertEqual(response['counter_party_image_url'], '')

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    @patch('backend.views.userviews.userviews.get_device')
    def test_image_url_is_returned(self, get_device, wc_contact, get_wc_token):
        sender_id = 'mysenderid'
        user = get_device.return_value.user
        user.wc_id = sender_id
        transfer = self._make_transfer(sender_id=sender_id)
        wc_contact.return_value.json.return_value = transfer
        request = self._make_request()
        image_url = 'myimageurl'
        mock_filter = request.dbsession.query.return_value.filter.return_value
        mock_filter.first.return_value.image_url = image_url
        response = self._call(request)
        self.assertEqual(response['counter_party_image_url'], image_url)
