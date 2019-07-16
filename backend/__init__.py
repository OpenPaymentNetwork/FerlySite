from pyramid.config import Configurator
from backend.settings import FerlySettings
from backend.site import Site
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

    config.add_static_view(name='files', path=settings['webpack_dist_dir'])
    config.add_static_view(
        name='stripeform', path=os.path.join(here, 'stripeform'))
    config.add_request_method(Site, name='site', reify=True)
    config.add_request_method(FerlySettings, name='ferlysettings', reify=True)
    config.add_request_method(get_params)
    config.add_tween(
        'backend.ise.internalservererror.InternalServerErrorTween')
    config.include('backend.database')
    config.scan()
    return config.make_wsgi_app()
