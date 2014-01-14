import collections

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
