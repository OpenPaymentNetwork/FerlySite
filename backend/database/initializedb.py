import os
import sys
import transaction

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from backend.database import (
    get_engine,
    get_session_factory,
    get_tm_session,
    )
from backend.database.meta import all_seq_names
from backend.database.meta import Base
from backend.database.models import SequenceKey


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s staging.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)

    engine = get_engine(settings)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)
        existing_seq_names = set(
            seq_name for (seq_name,) in dbsession.query(
                SequenceKey.seq_name).filter_by(key_index=0).all())
        for seq_name in all_seq_names.difference(existing_seq_names):
            # Add a reordering key for a new sequence.
            new_key = os.urandom(10)
            dbsession.add(SequenceKey(
                seq_name=seq_name,
                key_index=0,
                skip32_key=new_key))
        dbsession.flush()
