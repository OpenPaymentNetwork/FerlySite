
from pyramid.decorator import reify
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import Session


def get_metadata():
    from backend.database.models import Base
    return Base.metadata


def make_engine():
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
