##
## New API controller, forked from v3 core API
##

from __future__ import division, absolute_import

import datetime
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

from .new_logic import get_db_cursor
from .new_logic.auth import authenticate_request


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
    Format a multipart "Link" header content.

    :param links:
        links in a format similar to the one returned
        by Python requests, for example::

            {'first': {'rel': 'first',
              'url': '/api/ng/package?page=0'},
             'last': {'rel': 'last',
              'url': '/api/ng/package?page=10'},
             'next': {'rel': 'next',
              'url': '/api/ng/package?page=3'},
             'prev': {'rel': 'prev',
              'url': '/api/ng/package?page=1'}}
    """

    def iter_links_dict(links):
        for key, value in links.iteritems():
            if isinstance(value, basestring):
                value = {'url': value}
            value = value.copy()
            value['rel'] = key
            yield value

    def iter_links_list(links):
        for link in links:
            if not isinstance(link, dict):
                raise ValueError("links must be a list of dicts")
            yield link

    def iter_links(links):
        if isinstance(links, dict):
            return iter_links_dict(links)
        return iter_links_list(links)

    _links = []
    for item in iter_links(links):
        url = item.pop('url')
        parts = ['{key}="{value}"'.format(key=key, value=value)
                 for key, value in item.iteritems()]
        link = '<{0}>'.format(url)
        if len(parts):
            link = '{0}; {1}'.format(link, '; '.join(parts))
        _links.append(link)
    return ', '.join(_links)


def check_auth(perm):
    from functools import wraps

    def decorator(func):
        @wraps(func)
        def wrapped(self, *a, **kw):
            user = self._authenticate()
            perm_name = perm.format(*a, **kw)
            if not self._check_authz(user, perm_name):
                raise HTTPBadRequest("Not authorized to perform this action.")
            return func(self, *a, **kw)
        return wrapped
    return decorator


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

    def _authenticate(self):
        """
        :return:
            - User info (dict) if authentication was successful
            - None if not authentication was provided
        :raises:
            - HTTPForbidden if login failed
            - HTTPBadRequest if an unsupported auth method was requested
        """
        return authenticate_request(request)

    def _check_authz(self, user, action, obj=None):
        """
        Check authorization to perform an operation.

        :param user: the user object that want to perform the operation
        :param action: the action to be performed, composed of one of
            ('read', 'create', 'update', 'delete') and an object type.
        :param obj: target object, when applicable
        """
        if user is None:
            ## Anonymous can read everything, write nothing
            method = action.split(':')[0]
            return method == 'read'

        if user['sysadmin']:
            ## Sysadmins can do anything
            return True

        ## todo: add further permission checking

        return False

    @staticmethod
    def _get_paging_info(start, size, total):
        """
        Calculate pagination information (links to pages)

        :param start: current first item
        :param size: current page size
        :param total: total amount of items
        :return: a dict with the following keys:
            - ``first``  - "start" for the first page
            - ``prev``  - "start" for the prev page (if not already
                on the first page)
            - ``next``  - "start" for the next page (if not already
                on the last page)
            - ``last``  - "start" for the last page
        """
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

        ## Actually call the method
        retval = method(*method_args)

        ## todo: we need to catch HTTPErrors in order to serialize them
        ##       as json properly!
        ## todo: we also want to properly return 400/500s depending on
        ##       when an unhandled error occurred (how?)

        raw_data, status, headers = self._process_response(retval)

        response.headers.update(headers)
        response.status_int = status

        ## todo: check the appropriate serialization format..
        # data = json.dumps(raw_data)
        data = self._serialize_data(raw_data)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return data

    def _get_context_link(self, name):
        url = self._url('context/{0}'.format(name))
        return {
            'url': url,
            'rel': 'http://www.w3.org/ns/json-ld#context',
            'type': 'application/ld+json',
        }

    @staticmethod
    def _json_default(o):
        if isinstance(o, datetime.datetime):
            return o.strftime('%F %T')
        raise TypeError

    def _serialize_data(self, data):
        return json.dumps(data, default=self._json_default)

    def _process_response(self, retval):
        """
        :param retval:
            return value from an "action" method
        :return:
            a three-tuple: ``(data, status, headers)``
        """

        if isinstance(retval, tuple):
            if len(retval) == 1:
                data, status, headers = retval, 200, {}
            elif len(retval) == 2:
                data, status = retval
                headers = {}
            elif len(retval) == 3:
                data, status, headers = retval
            else:
                raise ValueError(
                    "Invalid retval: if a tuple, must have 1 to 3 elements")
            if not isinstance(status, int):
                raise TypeError("Invalid status code: must be an integer")
            if not isinstance(headers, dict):
                raise TypeError("Invalid headers: must be a dict")
            return data, status, headers
        else:
            return retval, 200, {}

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

    def _set_cors(self):
        ## Do not set CORS headers on every page!!
        pass

    @check_auth('read:help')
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

    @check_auth('read:help')
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

    @check_auth('read:info')
    def get_info_index(self):
        """Return some information about the current state"""

        # remove "confidential" information!
        user = self._authenticate()
        user.pop('apikey', None)
        user.pop('password', None)

        info = {
            'user': user,
        }
        return info

    @check_auth('read:context:id={0}')
    def get_context(name):
        from .jsonld import CONTEXTS, RDF_NAMESPACES
        try:
            context = CONTEXTS[name].copy()
        except KeyError:
            raise HTTPNotFound("No context with this name")
        context.update(RDF_NAMESPACES)
        return context

    @check_auth('read:package:index')
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

        ## Field names
        requested_fields = db_fields = None  # default set
        add_links = False  # whether to add links to items
        if 'fields' in request.params:
            requested_fields = request.params.getone('fields').split(',')
            db_fields = list(requested_fields)  # copy

        ## We always want to get object id
        if db_fields is not None:
            if 'id' not in db_fields:
                db_fields.append('id')

            ## The "link" field is generated
            if 'link' in db_fields:
                add_links = True
                db_fields.remove('link')

        ## Actually list packages
        result = list_packages(size=page_size, start=page_start,
                               fields=db_fields)

        if add_links:
            for res in result['results']:
                res['link'] = self._url('package/{0}'.format(res['id']))

        ## If only one field between (id, name, link) was required,
        ## just return it alone in a list
        if requested_fields is not None:
            if len(requested_fields) == 1 \
                    and (requested_fields[0] in ('id', 'name', 'link')):
                result['results'] = [
                    r[requested_fields[0]] for r in result['results']]

        ## Prepare the Link: header
        links = {}
        paging_info = self._get_paging_info(
            result['start'], result['size'], result['total'])
        for key, value in paging_info.iteritems():
            links[key] = self._url(
                'package', start=value, size=result['size'],
                fields=','.join(result['fields']))

        ## Prepare all headers
        headers = {
            'Link': _format_link_header(links),
            'x-page-size': result['size'],
            'x-page-start': result['start'],
            'x-result-total': result['total'],
        }

        return result['results'], 200, headers

    @check_auth('read:package:id={0}')
    def get_package(self, res_id):
        headers = {
            'Link': _format_link_header([
                self._get_context_link('package')]),
        }
        package = {}
        return package, 200, headers

    @check_auth('create:package')
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

    @check_auth('update:package:id={0}')
    def put_package(self, res_id):
        pass

    @check_auth('update:package:id={0}')
    def patch_package(self, res_id):
        pass

    @check_auth('delete:package:id={0}')
    def delete_package(self, res_id):
        pass

    ## Vocabulary CRUD
    ##------------------------------------------------------------

    @check_auth('read:vocabulary')
    def get_vocabulary_index(self):
        from .new_logic.tag import list_vocabularies
        return list_vocabularies()

    @check_auth('read:vocabulary:id={0}')
    def get_vocabulary(self, res_id):
        from .new_logic.tag import read_vocabulary_by_name
        return read_vocabulary_by_name(res_id)

    @check_auth('create:vocabulary')
    def post_vocabulary_index(self):
        from .new_logic.tag import create_vocabulary
        vocabulary_id = create_vocabulary()
        pass

    @check_auth('update:vocabulary')
    def put_vocabulary(self):
        pass

    @check_auth('delete:vocabulary:id={0}')
    def delete_vocabulary(self, res_id):
        from .new_logic.tag import read_vocabulary, delete_vocabulary
        vocab = read_vocabulary(res_id)
        delete_vocabulary(vocab['id'])
