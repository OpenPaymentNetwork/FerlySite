
from pyramid.decorator import reify
from pyramid.traversal import find_interface
from backend.database.models import Design


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
    
    @property
    def designs(self):
        return DesignCollection(self, 'designs')

    def __getitem__(self, name):
        if name == 'designs':
            return self.designs
        raise KeyError(name)


class DesignCollection:
    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name

    def __getitem__(self, name):
        site = find_interface(self, Site)
        design = site.dbsession.query(Design).get(name)
        if design is not None:
            design.__parent__ = self
            design.__name__ = name
            return design
        else:
            raise KeyError(name)

