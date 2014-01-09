# -*- coding: utf-8 -*-

## Ckan New Generation API for Ckan 2.2

# try:
#     from collections import OrderedDict
# except ImportError:
#     from ordereddict import OrderedDict

from ckan.plugins import implements, SingletonPlugin, IRoutes
# import ckan.lib.base as base
# import ckan.plugins.toolkit as plugins_toolkit
import routes.mapper as routes_mapper

from ckanext.api_ng.api_controller import ApiNgController


## We would put this in the main ckan configuration, but
## apparently routes are generated *before* configuration
## is read, so that's not possible.. :(
API_NG_URL_PREFIX = '/api/ng/'


class ApiNgPlugin(SingletonPlugin):
    # implements(IConfigurable)
    implements(IRoutes)

    ## Implementation of IConfigurable
    ##------------------------------------------------------------

    # def configure(self, config):
    #     ## Retrieve custom URL prefix
    #     self.conf = {
    #         'url_prefix': config.get('api_ng.url_prefix', '/api/ng/'),
    #     }

    ## Implementation of IRoutes
    ##------------------------------------------------------------

    def _get_full_path(self, path):
        url_parts = filter(None, API_NG_URL_PREFIX.split('/'))
        parts = filter(None, path.split('/'))
        return '/' + '/'.join(url_parts + parts)

    def before_map(self, routes):
        controller = 'ckanext.api_ng.plugin:ApiNgController'

        #-------------------------------------------------------------------------------- # noqa
        # 120     with SubMapper(map, controller='api', path_prefix='/api{ver:/3|}',      # noqa
        # 121                    ver='/3') as m:
        # 122         m.connect('/action/{logic_function}', action='action',
        # 123                   conditions=GET_POST)
        #-------------------------------------------------------------------------------- # noqa

        ## This should do (pretty much)
        with routes_mapper.SubMapper(routes, controller=controller) as m:
            #m.connect('/api/ng/{path_info:.*}', action='action')
            m.connect('/api/ng/{logic_function}', action='action')

            # for name in ['package_list', 'package_get']:
            #     page_slug = name.replace('_', '-')
            #     page_path = self._get_full_path(page_slug)
            #     m.connect(name, page_path, action=name)
        return routes

    def after_map(self, routes):
        return routes
