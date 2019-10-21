import os
from pyramid.decorator import reify
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import Session


def get_metadata():
    from backend.database.models import Base
    return Base.metadata


def make_engine():
    if os.name == 'nt':
        return create_engine('postgresql://test:test1234@localhost/ferlyapitest')
    else:
        return create_engine('postgresql:///ferlyapitest')


class DBFixture:
    """Provide a short lived connection to a temporary database for testing.

    The database should be empty (no tables or other objects). The schema
    will be created inside a transaction that never commits.

    Create an instance of this class in setup_module().

    Test modules using this class should contain the following code:

        from package.testing import DB

        def setup_module():
            global dbfixture
            dbfixture = DBFixture()

        def teardown_module():
            dbfixture.close_fixture()

        class TestX(unittest.TestCase):
            def setUp(self):
                self.dbsession, self.close_session = dbfixture.begin_session()

            def tearDown(self):
                self.close_session()

    This pattern lets test methods share the temporary database schema
    to reduce the number of times the schema needs to be created.
    """

    def begin_session(self):
        """Start a session. Return (dbsession, close_session).

        """
        connection = self.connection
        nested_transaction = connection.begin_nested()
        dbsession = Session(connection)

        def close_session():
            dbsession.close()
            nested_transaction.rollback()

        return dbsession, close_session

    @reify
    def engine(self):
        return make_engine()

    @reify
    def connection(self):
        metadata = get_metadata()
        connection = self.engine.connect()
        self.transaction = connection.begin()
        metadata.create_all(connection)
        return connection

    def close_fixture(self):
        """Abort the transaction and drop the connection.

        Call this in teardown_module().
        """
        self_vars = vars(self)
        connection = self_vars.get('connection')
        if connection is not None:
            self.transaction.rollback()
            connection.close()
            del self.connection
            del self.transaction
        engine = self_vars.get('engine')
        if engine is not None:
            engine.dispose()
            del self.engine


def add_device(
        dbsession,
        username='defaultusername',
        first_name='defaultfirstname',
        last_name='defaultlastname',
        wc_id='11',
        deviceToken=b'defaultdeviceToken0defaultdeviceToken0'):
    """Add a Customer and Device to the database."""
    from backend.database.models import Customer, Device
    import hashlib
    customer = Customer(
        wc_id=wc_id,
        first_name=first_name,
        last_name=last_name,
        username=username,
    )
    dbsession.add(customer)
    dbsession.flush()  # Assign customer.id

    if not isinstance(deviceToken, bytes):
        deviceToken = deviceToken.encode('utf-8')
    device = Device(
        token_sha256=hashlib.sha256(deviceToken).hexdigest(),
        customer_id=customer.id,
    )
    dbsession.add(device)
    dbsession.flush()  # Assign device.id

    return [device, customer]

def add_card_request(
        dbsession,
        customer_id='11',
        name='defaultname'):
    """Add a CardRequest to the database."""
    from backend.database.models import CardRequest
    import hashlib

    CardRequest = CardRequest(
        customer_id=customer_id,
        name=name,
        original_line1 = "test",
        original_city = "test",
        original_state = "test",
        original_zip_code = "84321",
        # line1, line2, city, state, and zip_code are normalized by the USPS
        # address info service.
        line1 = "test",
        city = "test",
        state = "test",
        zip_code = "84321",
    )
    dbsession.add(CardRequest)
    dbsession.flush() 

    return CardRequest

def add_deviceForCustomer11(
        dbsession,
        username='defaultusername',
        first_name='defaultfirstname',
        last_name='defaultlastname',
        wc_id='11',
        deviceToken=b'defaultdeviceToken0defaultdeviceToken0'):
    """Add a Customer and Device to the database."""
    from backend.database.models import Customer, Device
    import hashlib

    customer = Customer(
        id = '32',
        wc_id=wc_id,
        first_name=first_name,
        last_name=last_name,
        username=username,
    )
    dbsession.add(customer)
    dbsession.flush()  # Assign customer.id

    if not isinstance(deviceToken, bytes):
        deviceToken = deviceToken.encode('utf-8')
    device = Device(
        token_sha256=hashlib.sha256(deviceToken).hexdigest(),
        customer_id=customer.id,
    )
    dbsession.add(device)
    dbsession.flush()  # Assign device.id

    return [device, customer]