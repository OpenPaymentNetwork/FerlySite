
from backend.api_schemas import to_datetime
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
    before_created_str = params.get('before_created')
    before_created = None
    if before_created_str:
        try:
            before_created = to_datetime(before_created_str)
        except ValueError:
            pass
    limit = int(params.get('limit', 1000))
    show_downloaded = bool(params.get('show_downloaded', False))

    q = request.dbsession.query(CardRequest)

    if not show_downloaded:
        q = q.filter(CardRequest.downloaded == null)

    if before_created:
        q = q.filter(CardRequest.created < before_created)

    q = q.order_by(CardRequest.created.desc()).limit(limit + 1)

    rows = q.all()
    return {
        'rows': rows[:limit],
        'limit': limit,
        'show_downloaded': show_downloaded,
        'more': len(rows) > limit,
    }
