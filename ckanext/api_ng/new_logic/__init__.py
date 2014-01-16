import collections
import uuid

from ckan.common import c
import ckan.model


DEFAULT_PAGE_SIZE = 20


def get_context():
    return {
        'api_version': 3,
        'auth_user_obj': c.userobj,
        'model': ckan.model,
        'session': ckan.model.Session,
        'user': c.user or c.author,
    }


class LazyContext(collections.Mapping):
    """
    Lazy "context" object, for use in functions requiring
    a context. Hopefully, we're supporting all the possibly
    needed keys.
    """

    _ctx_keys = []

    def _create_context(self):
        return get_context()

    @property
    def _context(self):
        ctx = getattr(self, '_cached_context', None)
        if ctx is None:
            ctx = self._cached_context = self._create_context()
        return ctx

    def __iter__(self):
        return iter(self._context)

    def __getitem__(self, name):
        return self._context[name]

    def __len__(self):
        return len(self._context)


def get_db_connection_params():
    """
    Parse the SQLAlchemy DB URL into a dictionary
    suitable for psycopg2 connection.
    """
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


def get_db():
    """Get connection to the main database"""
    ## todo: use connection pooling
    import psycopg2
    params = get_db_connection_params()
    return psycopg2.connect(**params)


def get_db_cursor():
    """Return a DictCursor on the main database"""
    import psycopg2.extras
    return get_db().cursor(cursor_factory=psycopg2.extras.DictCursor)


def generate_id():
    """Return an UUID suitable for use in database"""
    return str(uuid.uuid4())
