from backend.models.site import API
from backend.models.site import Site
from backend.models.site import Static
from colander import Invalid
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.httpexceptions import HTTPServiceUnavailable
from pyramid.response import FileResponse
from pyramid.view import notfound_view_config
from pyramid.view import view_config
import os
import pyramid.httpexceptions as exc


@view_config(name='version', context=API, renderer='json')
def test(request):
    return {'version': '0.0.0'}


@view_config(name='', context=Site)
def index_html(request):
    webpack_dist_dir = request.ferlysettings.webpack_dist_dir
    fn = os.path.join(webpack_dist_dir, 'index.html')
    return FileResponse(
        fn,
        request=request,
        cache_max_age=600,
        content_type='text/html;charset=utf-8')


@view_config(context=Static)
def static_file(request):
    webpack_dist_dir = request.ferlysettings.webpack_dist_dir
    fn = os.path.join(webpack_dist_dir, *request.traversed[1:])
    if not os.path.isfile(fn):
        raise exc.HTTPNotFound()
    return FileResponse(
        fn,
        request=request,
        cache_max_age=600)


@notfound_view_config(renderer='json')
def notfound(request):
    """Render index.html for everything else.

    The frontend code will route appropriately.
    """
    if request.path.startswith('/api/'):
        request.response.status = HTTPNotFound.code
        return {
            'error': 'not_found',
            'error_description': 'The resource could not be found.',
        }

    webpack_dist_dir = request.ferlysettings.webpack_dist_dir
    fn = os.path.join(webpack_dist_dir, 'index.html')
    return FileResponse(
        fn,
        request=request,
        cache_max_age=600)


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
    return {'error': 'wingcash_unavailable'}
