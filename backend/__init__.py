from pyramid.config import Configurator
from backend.settings import FerlySettings
from backend.models.site import Site
from backend.utils import get_params


def main(global_config, **settings):
    """This function returns a Pyramid WSGI application."""

    def make_root(request):
        return request.site

    settings['env_file'] = global_config['__file__'].split('/')[-1]

    config = Configurator(
        root_factory=make_root,
        settings=settings,
    )

    config.add_request_method(Site, name='site', reify=True)
    config.add_request_method(FerlySettings, name='ferlysettings', reify=True)
    config.add_request_method(get_params)
    config.add_tween(
        'backend.ise.internalservererror.InternalServerErrorTween')
    config.include('backend.models')
    config.scan()
    return config.make_wsgi_app()
