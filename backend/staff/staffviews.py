
from backend.database.models import CardRequest
from backend.database.models import Customer
from backend.database.models import Design
from backend.database.models import Device
from backend.database.models import now_utc
from backend.param import to_datetime
from backend.site import StaffSite
from backend.staff.staffauth import authenticate_token
from io import StringIO
from pyramid.csrf import check_csrf_token
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.response import Response
from pyramid.view import (
    view_config,
    view_defaults
    )
from sqlalchemy import func
import csv
import logging
import colander
import deform.widget
from deform import ValidationFailure
from backend.site import DesignCollection

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



class design(object):
    def __init__(self, designs, request):
        self.request = request
        self.designs = designs
    
    @property
    def design_form(self):
        schema = DesignPage()
        return deform.Form(schema, buttons=('submit',))

    @property
    def reqts(self):
        return self.design_form.get_widget_resources()
    
    @view_config(
        name='',
        context=DesignCollection,
        renderer = 'templates/designs.pt')
    def designs_view(self):
        authenticate_token(self.request, require_group='FerlyAdministrators')
        rows = (
            self.request.dbsession.query(Design)
            .order_by(Design.title, Design.id)
            .all())
        parent = self.designs
        for row in rows:
            row.__parent__ = parent
            row.__name__ = str(row.id)
        #appstruct = {'title': rows[0].title}
        #print(type(rows[0].title))
        #form = self.design_form.render(appstruct)
        return {
            'parent': parent,
            'rows': rows,
            'breadcrumbs': [
                {
                    'url': self.request.resource_url(self.designs.__parent__),
                    'title': "Ferly Staff",
                }, {
                    'url': self.request.resource_url(self.designs),
                    'title': "Designs",
                },
            ],
        }

class DesignPage(colander.MappingSchema):
    title = colander.SchemaNode(colander.String(), title='Title')
    wc_id = colander.SchemaNode(colander.String(), title='OPN Note Design')
    distribution_id = colander.SchemaNode(colander.String(), title='Distribution Plan')
    listable = colander.SchemaNode(colander.Bool(), title='Listable', missing =False)
    logo_image_url = colander.SchemaNode(colander.String(), title='Logo Image URL', missing='')
    wallet_image_url = colander.SchemaNode(colander.String(), title='Wallet Image URL', missing='')
    fee = colander.SchemaNode(colander.Decimal(), title='Fee')
    authorized_merchant = colander.SchemaNode(colander.Bool(), title='Authorized Merchant', missing =False)

@view_config(
    name = 'edit',
    context=Design,
    renderer='templates/designsEdit.pt'
)
def edit(design, request):
    authenticate_token(request, require_group='FerlyAdministrators')
    schema = DesignPage()
    form = deform.Form(schema, buttons=('submit',))
    if 'submit' in request.POST:
        controls = request.POST.items()
        template_values = {'breadcrumbs': []}
        try:
            appstruct = form.validate(controls)
        except ValidationFailure as e:
            template_values['form_rendered'] = e.render()
            return template_values
        else:
            design.distribution_id = appstruct['distribution_id']
            design.wc_id = appstruct['wc_id']
            design.title = appstruct['title']
            design.listable = appstruct['listable']
            design.logo_image_url = appstruct['logo_image_url']
            design.wallet_image_url = appstruct['wallet_image_url']
            design.fee = round(appstruct['fee'],2)
            design.authorized_merchant = appstruct['authorized_merchant']
            return HTTPSeeOther(location=request.resource_url(design.__parent__))
    appstruct = {
                'distribution_id': design.distribution_id,
                'wc_id': design.wc_id,
                'title': design.title,
                'listable': design.listable,
                'logo_image_url': design.logo_image_url,
                'wallet_image_url': design.wallet_image_url,
                'fee': design.fee,
                'authorized_merchant': design.authorized_merchant
        }
    return {'form_rendered': form.render(appstruct), 'breadcrumbs': []}

@view_config(
name = 'add',
context=DesignCollection,
renderer='templates/designsAdd.pt'
)
def add(designCollection, request):
    authenticate_token(request, require_group='FerlyAdministrators')
    schema = DesignPage()
    form = deform.Form(schema, buttons=('submit',))
    if 'submit' in request.POST:
        controls = request.POST.items()
        template_values = {'breadcrumbs': []}
        try:
            appstruct = form.validate(controls)
        except ValidationFailure as e:
            template_values['form_rendered'] = e.render()
        else:
            dbsession = request.dbsession
            myNewDesign = Design(
                distribution_id = appstruct['distribution_id'],
                wc_id = appstruct['wc_id'],
                title = appstruct['title'],
                listable = appstruct['listable'],
                logo_image_url = appstruct['logo_image_url'],
                wallet_image_url = appstruct['wallet_image_url'],
                fee = round(appstruct['fee'],2),
                authorized_merchant = appstruct['authorized_merchant'],
                )
            myNewDesign.update_tsvector()
            dbsession.add(myNewDesign)
            return HTTPSeeOther(location=request.resource_url(designCollection))
        return template_values

    return {'form_rendered': form.render(), 'breadcrumbs': []}



@view_config(
    name='customers',
    context=StaffSite,
    renderer='templates/customers.pt')
def customers(staff_site, request):
    authenticate_token(request, require_group='FerlyAdministrators')
    params = request.params
    before_created = get_before_created(params)
    limit = int(params.get('limit', 1000))

    q = (
        request.dbsession.query(
            Customer, func.max(Device.last_used), func.array_agg(Device.os))
        .outerjoin(Device, Device.customer_id == Customer.id))

    if before_created:
        q = q.filter(Customer.created < before_created)

    rows = (
        q
        .group_by(Customer.id)
        .order_by(Customer.created.desc())
        .limit(limit + 1)
        .all())

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
