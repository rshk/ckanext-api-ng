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

    @property
    def _api_ng_url_prefix(self):
        from pylons import config
        return config.get('api_ng.base_url', '/api/ng/')

    # def _get_full_path(self, path):
    #     all_parts = self._api_ng_url_prefix.split('/') + path.split('/')
    #     return '/' + '/'.join(filter(None, all_parts))

    def before_map(self, routes):
        controller = 'ckanext.api_ng.api_controller:ApiNgController'

        #----- config/routing.py -------------------------------------------------------- # noqa
        # 120     with SubMapper(map, controller='api', path_prefix='/api{ver:/3|}',      # noqa
        # 121                    ver='/3') as m:
        # 122         m.connect('/action/{logic_function}', action='action',
        # 123                   conditions=GET_POST)
        #-------------------------------------------------------------------------------- # noqa

        with routes_mapper.SubMapper(routes, controller=controller) as m:
            #m.connect('/api/ng/{path_info:.*}', action='action')
            # m.connect(self._api_ng_url_prefix + '{logic_function}/{extra:.*}') # noqa
            m.connect(self._api_ng_url_prefix + '{action}')

        return routes

    def after_map(self, routes):
        return routes
