
from backend.staff.staffauth import resolve_token
from backend.site import StaffSite
from pyramid.view import view_config
import logging

log = logging.getLogger(__name__)


@view_config(
    name='',
    context=StaffSite,
    renderer='templates/staffhome.pt')
def staffhome(staff_site, request):
    resolve_token(request)
    return {}
