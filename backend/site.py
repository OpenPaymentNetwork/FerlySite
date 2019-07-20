
from pyramid.decorator import reify


class Site:
    __parent__ = None
    __name__ = None

    def __init__(self, request):
        self.dbsession = request.dbsession

    def __getitem__(self, name):
        if name == 'api':
            return self.api
        elif name == 'staff':
            return self.staff
        raise KeyError(name)

    @reify
    def api(self):
        return API(self, 'api')

    @reify
    def staff(self):
        return StaffSite(self, 'staff')


class API:
    def __init__(self, site, name):
        self.__parent__ = site
        self.__name__ = name


class StaffSite:
    def __init__(self, site, name):
        self.__parent__ = site
        self.__name__ = name
