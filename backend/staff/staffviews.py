
from backend.api_schemas import to_datetime
from backend.database.models import CardRequest
from backend.database.models import Customer
from backend.database.models import Design
from backend.database.models import now_utc
from backend.site import StaffSite
from backend.staff.staffauth import authenticate_token
from io import StringIO
from pyramid.csrf import check_csrf_token
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.response import Response
from pyramid.view import view_config
import csv
import logging

log = logging.getLogger(__name__)
null = None


def get_before_created(params):
    s = params.get('before_created')
    if s:
        try:
            return to_datetime(s)
        except ValueError:
            log.warning(
                "Invalid before_created parameter; ignoring: %s", repr(s))
    return None


@view_config(
    name='',
    context=StaffSite,
    renderer='templates/staffhome.pt')
def staffhome(staff_site, request):
    authenticate_token(request, require_group='FerlyAdministrators')
    return {'breadcrumbs': []}


@view_config(
    name='card-requests',
    context=StaffSite,
    renderer='templates/card-requests.pt')
def card_requests(staff_site, request):
    authenticate_token(request, require_group='FerlyAdministrators')
    params = request.params
    before_created = get_before_created(params)
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
        'staff_site': staff_site,
        'breadcrumbs': [
            {
                'url': request.resource_url(staff_site),
                'title': "Ferly Staff",
            }, {
                'url': request.resource_url(staff_site, 'card-requests'),
                'title': "Card Requests",
            },
        ],
    }


@view_config(
    name='card-requests-download',
    context=StaffSite)
def card_requests_download(staff_site, request):
    check_csrf_token(request)
    authenticate_token(request, require_group='FerlyAdministrators')

    download_ids = set()
    for k, v in request.params.items():
        if k == 'download':
            download_ids.add(v)

    if download_ids:
        dbsession = request.dbsession
        rows = (
            dbsession.query(CardRequest)
            .filter(CardRequest.id.in_(download_ids))
            .order_by(CardRequest.created.desc())
            .all())
        f = StringIO()
        writer = csv.writer(f)  # Use the default 'excel' dialect

        # These column names are intended to be similar enough to the
        # the address list Excel template from:
        # https://www.avery.com/resources/my-mail-merge-address-list-excel.xls
        writer.writerow([
            "Name",
            "Street Address",
            "Street Address Line 2",
            "City",
            "State",
            "Zip Code",
        ])

        for row in rows:
            if row.id in download_ids:
                row.downloaded = now_utc
                writer.writerow([
                    row.name,
                    row.line1,
                    row.line2,
                    row.city,
                    row.state,
                    row.zip_code,
                ])

        f.seek(0)
        body = f.read().encode('utf8')
        headers = {
            'Content-Disposition': 'attachment; filename="addresses.csv"',
            'Content-Type': 'application/x-force-download',
            'Content-Length': '%d' % len(body)}
        return Response(body, headers=headers)

    # No download IDs specified.
    return HTTPSeeOther(request.resource_url(staff_site, 'card-requests'))


@view_config(
    name='designs',
    context=StaffSite,
    renderer='templates/designs.pt')
def designs_view(staff_site, request):
    authenticate_token(request, require_group='FerlyAdministrators')
    rows = (
        request.dbsession.query(Design)
        .order_by(Design.title, Design.id)
        .all())
    return {
        'rows': rows,
        'breadcrumbs': [
            {
                'url': request.resource_url(staff_site),
                'title': "Ferly Staff",
            }, {
                'url': request.resource_url(staff_site, 'designs'),
                'title': "Designs",
            },
        ],
    }


@view_config(
    name='customers',
    context=StaffSite,
    renderer='templates/customers.pt')
def customers(staff_site, request):
    authenticate_token(request, require_group='FerlyAdministrators')
    params = request.params
    before_created = get_before_created(params)
    limit = int(params.get('limit', 1000))

    q = request.dbsession.query(Customer)

    if before_created:
        q = q.filter(Customer.created < before_created)

    q = q.order_by(Customer.created.desc()).limit(limit + 1)

    rows = q.all()
    return {
        'rows': rows[:limit],
        'limit': limit,
        'more': len(rows) > limit,
        'staff_site': staff_site,
        'breadcrumbs': [
            {
                'url': request.resource_url(staff_site),
                'title': "Ferly Staff",
            }, {
                'url': request.resource_url(staff_site, 'customers'),
                'title': "Customers",
            },
        ],
    }
