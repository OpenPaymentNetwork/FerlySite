
from backend.staff.staffauth import authenticate_token
from backend.site import StaffSite
from pyramid.view import view_config
import logging

log = logging.getLogger(__name__)


@view_config(
    name='',
    context=StaffSite,
    renderer='templates/staffhome.pt')
def staffhome(staff_site, request):
    authenticate_token(request, require_group='FerlyAdministrators')
    return {}
