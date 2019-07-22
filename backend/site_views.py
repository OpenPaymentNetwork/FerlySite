from backend.site import API
from backend.site import Site
from colander import Invalid
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.httpexceptions import HTTPServiceUnavailable
from pyramid.response import FileResponse
from pyramid.view import notfound_view_config
from pyramid.view import view_config
import os


@view_config(name='version', context=API, renderer='json')
def version(request):
    return {
        'environment': request.ferlysettings.environment,
        'version': '0.0.0'
    }


@view_config(name='', context=Site)
def index_html(request):
    webpack_dist_dir = request.ferlysettings.webpack_dist_dir
    fn = os.path.join(webpack_dist_dir, 'index.html')
    return FileResponse(
        fn,
        request=request,
        cache_max_age=600,
        content_type='text/html;charset=utf-8')


@notfound_view_config(renderer='json')
def notfound(request):
    """Render index.html for everything else.

    The frontend code will route appropriately.
    """
    p = request.path
    if p.startswith('/api/') or p.startswith('/staff/'):
        return HTTPNotFound(json_body={
            'error': 'not_found',
            'error_description': 'The resource could not be found.',
        })

    return index_html(request)


@view_config(context=Invalid, renderer='json')
def invalid(context, request):
    if not context.children:
        return {'invalid': context.messages()}
    return {'invalid': context.asdict()}


@view_config(context=HTTPUnauthorized, renderer='json')
def unauthorized(context, request):
    # response = request.response
    # response.headers.update({'WWW-Authenticate': 'Basic realm="Ferly"'})
    return {'error': 'device_not_recognized'}


@view_config(context=HTTPServiceUnavailable, renderer='json')
def serviceunavailable(context, request):
    return {'error': 'service_unavailable'}


@view_config(context=HTTPForbidden, renderer='json')
def forbidden(context, request):
    if getattr(context.exception, 'staff_token_required', False):
        from backend.staff.staffauth import login_redirect
        return login_redirect(request)
    require_group = getattr(context.exception, 'staff_require_group', None)
    if require_group:
        desc = "You are not a member of the '%s' group" % require_group
        return HTTPForbidden(json_body={
            'error': 'forbidden',
            'error_description': desc,
        })
    return HTTPForbidden(json_body={'error': 'forbidden'})
