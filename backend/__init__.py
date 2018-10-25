from pyramid.config import Configurator
from backend.settings import FerlySettings
from backend.models.site import Site


def main(global_config, **settings):
    """This function returns a Pyramid WSGI application."""

    def make_root(request):
        return request.site

    config = Configurator(
        root_factory=make_root,
        settings=settings,
    )

    config.add_request_method(Site, name='site', reify=True)
    config.add_request_method(FerlySettings, name='ferlysettings', reify=True)
    config.include('backend.models')
    config.scan()
    return config.make_wsgi_app()
