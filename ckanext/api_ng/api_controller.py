##
## New API controller, forked from v3 core API
##

# import cgi
# import functools
import json
import logging

from webob.exc import HTTPNotFound, HTTPBadRequest

from ckan.common import request, response
#from ckan.common import _, c, request, response
# import ckan.lib.base as base
# import ckan.lib.helpers as h
import ckan.lib.navl.dictization_functions
import ckan.logic as logic
# import ckan.model as model

from pylons.controllers.core import WSGIController


log = logging.getLogger(__name__)

# shortcuts
get_action = logic.get_action
NotAuthorized = logic.NotAuthorized
NotFound = logic.NotFound
ValidationError = logic.ValidationError
DataError = ckan.lib.navl.dictization_functions.DataError


_DEFAULT = object()


def get_api_prefix():
    from pylons import config
    return config.get('api_ng.base_url', '/api/ng')


class ApiNgController(WSGIController):
    """
    Custom controller for the API.

    - Will figure out the method to use depending on http
      method and action name
    - Handles automatic serialization of content body
    - Perfoms all the required checks

    Methods are named {http_method}_{action} and can return:

    - a generic object (data)
    - a (data, status) tuple
    - a (data, status, headers) tuple

    ``data`` will be json-serialized if it's not a string
    """

    def _url(self, path):
        """Generate full (relative) URL for something"""
        prefix = getattr(self, '_url_prefix', None)
        if prefix is None:
            prefix = get_api_prefix()
            self._url_prefix = prefix
        return '/'.join((
            prefix.rstrip('/'),
            path.lstrip('/')))

    def dispatch(self, resource, res_id=None, related=None):
        """
        Will try to do one of the following calls, depending on the
        passed parameters:

        * {http_method}_{resource}_index()
        * {http_method}_{resource}({res_id})
        * {http_method}_{resource}_{related}({res_id})
        """

        http_method = request.method.lower()
        if res_id is None:
            method_name = '{0}_{1}_index'.format(http_method, resource)
            method_args = []
        elif related is None:
            method_name = '{0}_{1}'.format(http_method, resource)
            method_args = [res_id]
        else:
            method_name = '{0}_{1}_index'.format(http_method, resource)
            method_args = [res_id]

        try:
            method = getattr(self, method_name)
        except AttributeError:
            raise HTTPNotFound()

        kwargs = {}
        if res_id is not _DEFAULT:
            kwargs['res_id'] = res_id
        if related is not _DEFAULT:
            kwargs['related'] = related

        retval = method(*method_args)

        ## todo: we need to catch HTTPErrors in order to serialize them
        ##       as json properly!
        ## todo: we also want to properly return 400/500s depending on
        ##       when an unhandled error occurred

        raw_data, status, headers = self._process_response(retval)

        response.headers.update(headers)
        response.status_int = status
        data = json.dumps(raw_data)
        response.headers['content-type'] = 'application/json'
        return data

    def _process_response(self, response):
        if isinstance(response, tuple):
            if len(response) == 1:
                data, status, headers = response, 200, {}
            elif len(response) == 2:
                data, status = response
                headers = {}
            elif len(response) == 3:
                data, status, headers = response
            else:
                raise ValueError(
                    "Invalid response: if a tuple, must have 1 to 3 elements")
            if not isinstance(status, int):
                raise TypeError("Invalid status code: must be an integer")
            if not isinstance(headers, dict):
                raise TypeError("Invalid headers: must be a dict")
            return data, status, headers
        else:
            return response, 200, {}

    def _find_methods(self):
        ## todo: we could cache method names..
        reserved_methods = ['start_response', 'dispatch']
        for name in dir(self):
            if (name not in reserved_methods) \
                    and (not name.startswith('_')) \
                    and callable(getattr(self, name)):
                yield name

    def _expand_method_name(self, name):
        ## Convert method name back to "METHOD /path", for use
        ## in the documentation.
        parts = name.split('_')

        if len(parts) == 2:
            http_method, resource = parts
            return (parts[0].upper(),
                    '/{0}/{{id}}'.format(parts[1]))

        elif len(parts) == 3:
            if parts[2] == 'index':
                return (parts[0].upper(),
                        '/{0}'.format(parts[1]))

            return (parts[0].upper(),
                    '/{0}/{{id}}/{1}'.format(parts[1], parts[2]))

        else:
            raise ValueError("Invalid method name: {0}".format(name))

    def get_help_index(self):
        """
        Return documentation about available API resources.
        """

        method_docs = {}

        for name in self._find_methods():
            key = ' '.join(self._expand_method_name(name))

            import inspect
            method_docs[key] = {
                'help_url': self._url('/help/{0}'.format(name)),
                'doc': inspect.getdoc(getattr(self, name))
            }

        return method_docs

    def get_help(self, res_id):
        """Get help about a given api call"""
        if res_id not in self._find_methods():
            raise HTTPNotFound('No such method')

        import inspect
        method = getattr(self, res_id)
        return {
            'help_url': self._url('/help/{0}'.format(res_id)),
            'doc': inspect.getdoc(method),
            'title': ' '.join(self._expand_method_name(res_id)),
        }

    def get_package_index(self):
        return 'test'

    def get_hello_index(self):
        return 'hello ' + str(request.params)

    def post_hello_index(self):
        return 'HELLO'

    # def get_400(self):
    #     raise HTTPBadRequest('you did something wrong')

    # def get_402(self):
    #     return 'hello', 403, {'x-reason': 'notauthorized'}
