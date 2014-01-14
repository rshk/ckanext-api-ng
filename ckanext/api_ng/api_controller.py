##
## New API controller, forked from v3 core API
##

from __future__ import division

import json
import logging
import urllib

from webob.exc import HTTPNotFound, HTTPBadRequest, HTTPForbidden
import sqlalchemy
#from pylons.controllers.core import WSGIController

from ckan.common import request, response, c, _
from ckan.lib.base import BaseController
import ckan.lib.navl.dictization_functions
import ckan.lib.plugins
import ckan.logic as logic
import ckan.model as model


log = logging.getLogger(__name__)


MAX_PAGE_SIZE = 50
MIN_PAGE_SIZE = 1


def get_api_prefix():
    """
    Return the URL prefix for the NG api, reading
    from the api_ng.base_url configuration key.
    If none was specified, /api/ng/ will be used.
    """
    from pylons import config
    return config.get('api_ng.base_url', '/api/ng')


def _format_link_header(links):
    """
    Format a dictionary into value suitable for a ``Link:`` header.

    >>> _format_link_header({'hello': 'http://example.com'})
    <http://example.com>; rel=hello
    """
    _links = []
    for key, value in links.iteritems():
        ## WARNING: We are not escaping links: which is the
        ## proper way to handle the (rare) case in which there
        ## is a < or > symbol in the URL?
        _links.append('<{1}>; rel={0}'.format(key, value))
    return ', '.join(_links)


class ApiNgController(BaseController):
    """
    Custom controller for the API.

    - Will figure out the method to use depending on http
      method and action name
    - Handles automatic serialization of content body
    - Perfoms all the required checks

    Methods are named {http_method}_{action}_[{related}] and can return:

    - a generic object (data)
    - a (data, status) tuple
    - a (data, status, headers) tuple

    ``data`` will be json-serialized if it's not a string
    """

    def _url(self, path, **args):
        """Generate full (relative) URL for something"""
        prefix = getattr(self, '_url_prefix', None)
        if prefix is None:
            prefix = get_api_prefix()
            self._url_prefix = prefix
        path = '/'.join((
            prefix.rstrip('/'),
            path.lstrip('/')))
        if len(args):
            path += '?' + urllib.urlencode(args)
        return path

    def _get_db_connection_params(self):
        from pylons import config
        import urlparse
        db_url = config.get('sqlalchemy.url')
        db_url_parts = urlparse.urlparse(db_url)
        if db_url_parts.scheme != 'postgresql':
            raise ValueError("Invalid database scheme: " + db_url_parts.scheme)
        user_pass, host_port = db_url_parts.netloc.split('@')
        user, password = user_pass.split(':')
        if ':' in host_port:
            host, port = host_port.split(':')
            port = int(port)
        else:
            host, port = host_port, 5432
        dbname = db_url_parts.path.strip('/').split('/')[0]
        return dict(
            database=dbname,
            user=user,
            password=password,
            host=host,
            port=port)

    def _get_db(self):
        import psycopg2
        params = self._get_db_connection_params()
        return psycopg2.connect(**params)

    def _get_db_cursor(self):
        import psycopg2.extras
        return self._get_db().cursor(cursor_factory=psycopg2.extras.DictCursor)

    def _authenticate(self):
        """
        Figure out the user name and check that signature is valid.

        .. note::
            This will only work for "sysadmin" users, as there isn't any
            authorization check in place, at the moment..

        :return:
            the user object (as dict or dict-like), or None if the
            user is not authenticated.
        """
        import base64

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None  # Not authenticated

        auth_type, auth_payload = auth_header.split(' ', 1)

        if auth_type == 'Signature':
            raise NotImplementedError(
                "Signature authentication is not implemented yet")

            # from itsdangerous import Signer
            # username, signature = base64.decodestring(auth_payload).split(':')  # noqa
            # cur = self._get_db_cursor()
            # cur.execute('SELECT * FROM "user" WHERE name=%s AND sysadmin=True')  # noqa
            # user_obj = cur.fetchone()
            # if not user_obj:
            #     raise HTTPForbidden("Invalid username or signature")

            # ## Verify HMAC signature with user key
            # s = Signer(user_obj['apikey'])
            # itsok = s.verify_signature(request.body, signature)
            # if not itsok:
            #     raise HTTPForbidden("Invalid username or signature")

            # ## Let's just return the user object (dict-like)
            # return user_obj

        elif auth_type == 'Basic':
            ## Perform basic HTTP authentication, with ``user:apikey``
            ## base64(user:key)
            username, apikey = base64.decodestring(auth_payload).split(':')
            cur = self._get_db_cursor()
            cur.execute("""
            SELECT id, name, apikey, fullname, email, sysadmin
            FROM "user"
            WHERE name=%(username)s AND state='active' AND sysadmin=True;
            """, dict(username=username,))
            user_obj = cur.fetchone()
            if (not user_obj) or (user_obj['apikey'] != apikey):
                raise HTTPForbidden("Invalid username or API key")
            return dict(user_obj)

        else:
            raise HTTPBadRequest(
                "Unsupported authentication method: " + auth_type)

    @staticmethod
    def _get_paging_info(start, size, total):
        import math
        total_pages = int(math.ceil(total / size))
        current_page = int(start / size)
        last_page = total_pages - 1
        info = {}

        info['first'] = 0
        if current_page > 0:
            info['prev'] = (current_page - 1) * size
        if current_page < last_page:
            info['next'] = (current_page + 1) * size
        info['last'] = last_page * size
        return info

    def dispatch(self, resource, res_id=None, related=None):
        """
        Main entry point. This method is the one called by the router.
        From here, we will try to do further dispatching, based on
        http method and current path.

        Will try to do one of the following calls, depending on the
        passed-in parameters:

        * none:
          ``{http_method}_{resource}_index()``

        * only res_id:
          ``{http_method}_{resource}({res_id})``

        * both res_id and related:
          ``{http_method}_{resource}_{related}({res_id})``
        """

        ## todo: properly handle the HEAD method: if there isn't a proper
        ##       to handle it, just call ``get_`` and return just headers

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

        # ## Let's try to figure out which parameters are expected by the
        # ## method..
        # import inspect
        # method_argspec = inspect.getargspec(method)
        # args = method_argspec.args[1:]  # remove 'self' (and make a copy)

        # # Make space for positional arguments
        # for a in method_args:
        #     args.pop(0)

        # ## Now, we want to populate kwargs with attributes that might
        # ## be needed. If the function accepts generic kwargs, we will
        # ## just pass them all. Otherwise, we only return what is
        # ## actually needed..

        # extra_args = {
        #     'user': lambda: self._authenticate(),
        #     'context': lambda: self._get_context(),
        # }

        # kwargs = {}
        # if method_argspec.keywords is not None:
        #     args = list(extra_args.iterkeys())
        # for a in args:
        #     kwargs[a] = extra_args[a]()

        ## Actually call the method
        retval = method(*method_args)

        ## todo: we need to catch HTTPErrors in order to serialize them
        ##       as json properly!
        ## todo: we also want to properly return 400/500s depending on
        ##       when an unhandled error occurred

        raw_data, status, headers = self._process_response(retval)

        response.headers.update(headers)
        response.status_int = status

        ## todo: check the appropriate serialization format..
        data = json.dumps(raw_data)
        response.headers['Content-Type'] = 'application/json'
        return data

    def _process_response(self, response):
        """
        :param response: a response as returned by an API method
        :return: a three-tuple in the format ``(data, status, headers)``
        """

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
        """Find methods suitable to be exposed through the API"""

        ## todo: we could cache method names..
        reserved_methods = ['start_response', 'dispatch']
        for name in dir(self):
            if (name not in reserved_methods) \
                    and (not name.startswith('_')) \
                    and callable(getattr(self, name)):
                yield name

    def _expand_method_name(self, name):
        """
        Convert method name back to "METHOD /path", for use
        in the documentation.
        """

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

    # def _check_access(self, name, data_dict=None):
    #     """Wrapper around check_access, automatically getting context"""

    #     ## todo: which exception do this thing return?
    #     ## if that's the case, catch and reraise a 403
    #     context = self._get_context()
    #     return logic.check_access('package_list', context, data_dict)

    def _set_cors(self):
        ## Do not set CORS headers on every page!!
        pass

    def get_help_index(self):
        """Return documentation about available API resources"""

        import inspect

        method_docs = {}
        for name in self._find_methods():
            key = ' '.join(self._expand_method_name(name))
            method_docs[key] = {
                'help_url': self._url('/help/{0}'.format(name)),
                'doc': inspect.getdoc(getattr(self, name))}

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

    def get_info_index(self):
        """Return some information about the current state"""

        user = self._authenticate()

        # remove "confidential" information!
        user.pop('apikey', None)
        user.pop('password', None)

        info = {
            'user': user,
        }
        return info

    def get_package_index(self):
        """
        Return list of packages (datasets).

        :param start:
        :param size:
        """
        from .new_logic.package import list_packages

        # self._check_access('package_list')

        page_size, page_start = 20, 0
        if 'size' in request.params:
            page_size = int(request.params.getone('size'))
        if 'start' in request.params:
            page_start = int(request.params.getone('start'))

        ## Cap page size
        page_size = max(MIN_PAGE_SIZE, min(page_size, MAX_PAGE_SIZE))

        ## Actually list packages
        result = list_packages(size=page_size, start=page_start)

        ## Prepare the Link: header
        links = {}
        paging_info = self._get_paging_info(
            result['start'], result['size'], result['total'])
        for key, value in paging_info.iteritems():
            links[key] = self._url('package', start=value, size=result['size'])

        ## Prepare all headers
        headers = {
            'Link': _format_link_header(links),
            'x-page-size': result['size'],
            'x-page-start': result['start'],
            'x-result-total': result['total'],
        }

        return result['results'], 200, headers

    def get_package(self, res_id):
        pass

    def post_package_index(self):
        """
        Create a new dataset.
        Accepts the new dataset in the request body, as a json object.

        * Standard keys (name, title, author, author_email, maintainer,
            maintainer_email, notes, url) are just normal fields in the
            package table.

        * ``license_id`` -- id of the license to be used for this dataset.
            See ``/license`` for a complete list of supported licenses
        * ``state`` -- The dataset state. Supported values are 'active'
            and 'deleted'
        * ``type`` -- the package type. Defaults to 'dataset'.
        * ``resources`` -- a list of dictionaries to be added as resources
        * ``tags`` -- a list of tags to be added to the dictionary.
            Can be either a list of strings (tag names) or a list of
            dictionaries to be used as filters to search for tags.
        * ``extras`` -- either a dictionary or list of two-tuples,
            representing "extra" items.
        * ``groups`` -- either a list of strings (group names) or dicts
            used to match groups to associate with this package
        * ``organization_id`` -- id of the organization to be associated
            with this package
        """

        user = self._authenticate()
        if user is None:
            raise HTTPForbidden("You must logged-in to perform this operation")

        try:
            ## todo: check request Content-type too?
            data = json.loads(request.body)
        except:
            raise HTTPBadRequest('Unable to parse request body')

        ## First, check that the user is allowed to create datasets
        self._check_access('package_create', data)

        user = self._get_user()

        data['creator_user_id'] = user.id

        ## todo: create this package

        return data

    def put_package(self, res_id):
        pass

    def patch_package(self, res_id):
        pass

    def delete_package(self, res_id):
        pass

    # def get_hello_index(self):
    #     return 'hello ' + str(request.params)

    # def post_hello_index(self):
    #     return 'HELLO'

    # def get_400(self):
    #     raise HTTPBadRequest('you did something wrong')

    # def get_402(self):
    #     return 'hello', 403, {'x-reason': 'notauthorized'}
