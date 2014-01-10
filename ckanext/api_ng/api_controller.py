##
## New API controller, forked from v3 core API
##

import cgi
import functools
import json
import logging

from ckan.common import _, c, request, response
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.lib.navl.dictization_functions
import ckan.logic as logic
import ckan.model as model

from pylons.controllers.core import WSGIController


log = logging.getLogger(__name__)

# shortcuts
get_action = logic.get_action
NotAuthorized = logic.NotAuthorized
NotFound = logic.NotFound
ValidationError = logic.ValidationError
DataError = ckan.lib.navl.dictization_functions.DataError


IGNORE_FIELDS = ['q']
CONTENT_TYPES = {
    'text': 'text/plain;charset=utf-8',
    'html': 'text/html;charset=utf-8',
    'json': 'application/json;charset=utf-8',
}

_DEFAULT = object()


def api_method(func=None, methods=_DEFAULT):
    """
    Decorator for API methods, providing some extra
    facilities, such as json serialization and adding
    headers.
    """
    if methods is _DEFAULT:
        methods = ['GET']

    def decorator(func):
        @functools.wraps(func)
        def new_function(environ, start_response):
            return wrap_call(request, response, func, methods,
                             environ, start_response)

    if func is None:
        return decorator
    return decorator(func)


def wrap_call(request, response, func, methods, environ, start_response):
    """
    Wrap calling of the actual controller action.

    This will:
    """

    ## Check whether method is allowed
    if request.method not in methods:
        response.status_int = 405  # Method not allowed
        response.headers['allow'] = ', '.join(methods)
        return json.dumps({
            'message': 'Method not allowed. You can use: {0}'
            .format(', '.join(methods))
        })

    ## Todo: here seems a nice place to check authentication
    ##       if needed..
    ## Todo: we could also perform some authorization checks..

    result = func()

    body, status, headers = '', 200, {}
    if isinstance(result, tuple):
        if len(result) == 1:
            body = result[0]

        elif len(result) == 2:
            body, status = result

        elif len(result) == 3:
            body, status, headers = result

        else:
            raise ValueError(
                "API methods should return a one, two or three-tuple")
    else:
        ## Single value returned -> body
        body = result

    ## Validate result from function
    if not isinstance(status, int):
        raise TypeError("Invalid http status (int expected)")
    if not isinstance(headers, dict):
        raise TypeError("Invalid headers object (dict expected)")

    if not isinstance(body, basestring):
        import json
        body = json.dumps(body)
        headers['content-type'] = 'application/json'

    ## update response, return body
    response.status_int = status
    response.headers.update(headers)
    return body


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

    def __call__(self, environ, start_response):
        ## 1. Figure out which method to call
        ## 2. Do authentication stuff
        ## 3. Check authorization, when applicable
        ## 4. Call the method
        ## 5. Process response data, send back to client

        # todo: we need to authenticate the user
        # todo: we need to perform authorization checks

        self._identify_user()  # todo: check this one

        try:
            context = {
                'model': model,
                'user': c.user or c.author,
                'auth_user_obj': c.userobj,
            }

            # ..mh?
            logic.check_access('site_read', context)

        except NotAuthorized:
            response_msg = self._finish(
                403,  _('Not authorized to see this page'))

            # Call start_response manually instead of the parent __call__
            # because we want to end the request instead of continuing.
            response_msg = response_msg.encode('utf8')
            body = '%i %s' % (response.status_int, response_msg)

            start_response(body, response.headers.items())
            return [response_msg]

        # avoid status_code_redirect intercepting error responses
        environ['pylons.status_code_redirect'] = True

        start_response(200, {'content-type': 'text/plain'}.items())
        return ['hello']

        ## Call the original WSGIController.__call__()
        ## Beware: there is a custom __call__ from ckan in between,
        ## that does stuff!
        return base.BaseController.__call__(self, environ, start_response)

    def _get_current_user(self, request):
        """Try to authenticate the user, by checking for an API key"""
        pass

    def _get_action_method(self, request, action):
        pass

    def get_debug(self):
        return {'message': 'hello get'}, 200, {'content-type': 'text/plain'}

    def post_debug(self):
        return {'message': 'hello post'}, 200, {'content-type': 'text/plain'}
