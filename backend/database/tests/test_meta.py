

from backend.testing import DBFixture
import unittest


def setup_module():
    global dbfixture
    dbfixture = DBFixture()


def teardown_module():
    dbfixture.close_fixture()


class TestStringSequencer(unittest.TestCase):

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from ..meta import string_sequencer
        return string_sequencer(*args, **kw)

    def test_20_random_ids_should_be_unique(self):
        fn = self._call('customer_seq')  # Piggyback an existing sequence
        unique = set()
        for i in range(20):
            value = list(self.dbsession.execute(fn))[0][0]
            # The length of IDs in new sequences is 8 hex characters (32 bits).
            self.assertEqual(8, len(value))
            unique.add(value)
        self.assertEqual(20, len(unique))

    def test_32_bit_sequence_value(self):
        # The length of IDs expands slowly as needed.
        fn = self._call('customer_seq')
        self.dbsession.execute(
            "select setval('customer_seq', 2147483649)")  # (1 << 31) + 1
        value = list(self.dbsession.execute(fn))[0][0]
        self.assertEqual(9, len(value))
        self.assertEqual('1', value[0])

    def test_37_bit_sequence_value(self):
        fn = self._call('customer_seq')
        self.dbsession.execute(
            "select setval('customer_seq', 68719476737)")  # (1 << 36) + 1
        value = list(self.dbsession.execute(fn))[0][0]
        self.assertEqual(10, len(value))
        self.assertEqual('20', value[:2])

    def test_63_bit_sequence_value(self):
        fn = self._call('customer_seq')
        self.dbsession.execute(
            "select setval('customer_seq', 4611686018427387904)")  # 1 << 62
        value = list(self.dbsession.execute(fn))[0][0]
        self.assertEqual(16, len(value))

    def test_max_bit_sequence_value(self):
        fn = self._call('customer_seq')
        # The max sequence value is 1 << 63 - 1.
        # The sequence will increment in next_value(), so dial the current
        # value back accordingly.
        self.dbsession.execute(
            "select setval('customer_seq', 9223372036854775807 - 1047311)")
        value = list(self.dbsession.execute(fn))[0][0]
        self.assertEqual(16, len(value))
