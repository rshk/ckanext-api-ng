# -*- coding: utf-8 -*-

##------------------------------------------------------------
## Ckan New Generation API for Ckan 2.2
##------------------------------------------------------------

from ckan.plugins import implements, SingletonPlugin, IRoutes
import routes.mapper as routes_mapper

from ckanext.api_ng.api_controller import ApiNgController  # noqa


class ApiNgPlugin(SingletonPlugin):
    implements(IRoutes)

    ## Implementation of IRoutes
    ##------------------------------------------------------------

    def before_map(self, routes):
        from ckanext.api_ng.api_controller import get_api_prefix
        controller = 'ckanext.api_ng.api_controller:ApiNgController'

        with routes_mapper.SubMapper(routes, controller=controller,
                                     path_prefix=get_api_prefix()) as m:
            m.connect('/{resource}', action='dispatch')
            m.connect('/{resource}/{res_id}', action='dispatch')
            m.connect('/{resource}/{res_id}/{related}', action='dispatch')

        return routes

    def after_map(self, routes):
        return routes
