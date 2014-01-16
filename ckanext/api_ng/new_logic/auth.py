from __future__ import absolute_import

from webob.exc import HTTPForbidden, HTTPBadRequest

from . import get_db_cursor


def authenticate_request(request):
    """
    Authenticate a request, returning an user object if
    authentication was successful or None if no authentication
    information was provided (anonymous user).
    """
    import base64

    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None  # Not authenticated

    try:
        auth_type, auth_payload = auth_header.split(' ', 1)
    except:
        raise HTTPBadRequest("Bad Authorization header supplied")

    if auth_type == 'Basic':
        ## Perform basic HTTP authentication, with ``user:apikey``
        ## base64(user:key)
        username, apikey = base64.decodestring(auth_payload).split(':')
        return basic_authentication(username, apikey)

    raise HTTPBadRequest("Unsupported authorization method: {0!r}"
                         .format(auth_type))


def basic_authentication(username, apikey):
    cur = get_db_cursor()
    cur.execute("""
    SELECT id, name, apikey, fullname, email, sysadmin
    FROM "user"
    WHERE name=%(username)s AND state='active' AND sysadmin=True;
    """, dict(username=username,))
    user_obj = cur.fetchone()
    if (not user_obj) or (user_obj['apikey'] != apikey):
        raise HTTPForbidden("Invalid username or API key")
    return dict(user_obj)
