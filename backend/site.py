from pyramid.decorator import reify
from weakref import ref


class Site(object):
    __parent__ = None
    __name__ = None

    def __init__(self, request):
        self.dbsession = request.dbsession
        self.request_ref = ref(request)

    def __getitem__(self, name):
        if name == 'api':
            return self.api
        elif name == 'files':
            return Static(self, name)
        raise KeyError(name)

    @reify
    def api(self):
        return API(self)


class Static(object):
    def __init__(self, site, name):
        self.__parent__ = site
        self.__name__ = name

    def __getitem__(self, name):
        return self


class API(object):
    def __init__(self, site):
        self.__parent__ = site
        self.__name__ = 'api'
        self.request_ref = site.request_ref
