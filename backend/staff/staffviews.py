
from backend.database.models import CardRequest
from backend.staff.staffauth import authenticate_token
from backend.site import StaffSite
from pyramid.view import view_config
import logging

log = logging.getLogger(__name__)
null = None


@view_config(
    name='',
    context=StaffSite,
    renderer='templates/staffhome.pt')
def staffhome(staff_site, request):
    authenticate_token(request, require_group='FerlyAdministrators')
    return {}


@view_config(
    name='card-requests',
    context=StaffSite,
    renderer='templates/card-requests.pt')
def card_requests(staff_site, request):
    authenticate_token(request, require_group='FerlyAdministrators')
    params = request.params
    offset = int(params.get('offset', 0))
    limit = int(params.get('limit', 1000))
    show_downloaded = bool(params.get('show_downloaded', False))

    q = request.dbsession.query(CardRequest)

    if not show_downloaded:
        q = q.filter(CardRequest.downloaded == null)

    q = q.order_by(CardRequest.created.desc())

    if offset:
        q = q.offset(offset)
    q = q.limit(limit)

    rows = q.all()
    return {'rows': rows}
