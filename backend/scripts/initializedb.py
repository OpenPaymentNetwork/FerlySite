import os
import sys
import transaction

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models.meta import Base
from ..models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    )
from ..models import User
from ..models import Device
from ..models import Design


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
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

        brad = User(
            wc_id='5721935278',
            title='Brad Wilkes',
            image_url='https://scontent-sjc3-1.xx.fbcdn.net/v' +
                      '/t1.0-9/17862330_1163112860477719_87737977638459' +
                      '11478_n.jpg?_nc_cat=0&oh=1ee52b76a4851bfd2566d59' +
                      '4dd503ae7&oe=5B7A48D2',
            expo_token='ExponentPushToken[caJCr4Clchz7DDWj8RL5dr]')
        bradley = User(
            wc_id='5896656681',
            title='Bradley Wilkes',
            image_url='https://media.licdn.com/dms/image/C4E0' +
                      '3AQGbM0NQJWkp2w/profile-displayphoto-shrink_200_' +
                      '200/0?e=1529226000&v=beta&t=b-jG7N4n81RCuTyFc1BV' +
                      '-77N0u0V4UxyB84ncbOXP8w',
            expo_token='ExponentPushToken[yQf7p8NRyNWhrx8n-rTYno]')
        ferly = User(wc_id='5820583106', title='Ferly')

        dbsession.add(brad)
        dbsession.add(bradley)
        dbsession.add(ferly)
        dbsession.flush()

        brad_device = Device(
            user_id=brad.id, device_id='bc9e29e6-4076-4317-a572-92d6accae312')
        bradley_device = Device(
            user_id=bradley.id,
            device_id='464B1D5E-1BB5-464B-B694-E5649BD39AAB')
        dbsession.add(brad_device)
        dbsession.add(bradley_device)

        apple = Design(
            title='Apple',
            wc_id='6296329800',
            image_url='http://www.stickpng.com/assets' +
                      '/images/580b57fcd9996e24bc43c516.png')
        amazon = Design(
            title='Amazon',
            wc_id='7155469021',
            image_url='https://png.icons8.com/windows/1600/amazon.png')
        dbsession.add(apple)
        dbsession.add(amazon)
