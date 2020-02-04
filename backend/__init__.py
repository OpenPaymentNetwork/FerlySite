
from backend.settings import FerlySettings
from backend.site import Site
from pyramid.config import Configurator
from pyramid.csrf import CookieCSRFStoragePolicy
from pyramid.settings import asbool
import os.path

here = os.path.abspath(os.path.dirname(__file__))


def get_params(request, schema):
    if getattr(request, 'content_type', None) == 'application/json':
        param_map = request.json_body
    else:
        param_map = request.params
    return schema.bind(request=request).deserialize(param_map)


def main(global_config, **settings):
    """This function returns a Pyramid WSGI application."""

    def make_root(request):
        return request.site

    settings['env_file'] = global_config['__file__'].split('/')[-1]

    config = Configurator(
        root_factory=make_root,
        settings=settings,
    )
    config.set_csrf_storage_policy(CookieCSRFStoragePolicy(
        secure=asbool(settings.get('secure_cookie', True))))

    config.add_static_view(name='doc', path=settings['apidoc_dir'])
    config.add_static_view('static', 'deform:static')
    config.add_static_view(
        name='stripeform', path=os.path.join(here, 'stripeform'))
    config.add_request_method(Site, name='site', reify=True)
    config.add_request_method(FerlySettings, name='ferlysettings', reify=True)
    config.add_request_method(get_params)
    config.add_tween(
        'backend.ise.internalservererror.InternalServerErrorTween')
    config.add_tween(
        'backend.tweens.HeaderTween')
    config.include('backend.database')
    config.include('pyramid_chameleon')
    config.scan()
    return config.make_wsgi_app()
