"""New methods for package CRUD"""

from __future__ import absolute_import

from ckan.common import request, c
import ckan.model
from ckan.logic import check_access

from sqlalchemy import and_
from sqlalchemy.sql import select, func
from sqlalchemy.orm import aliased

from . import DEFAULT_PAGE_SIZE, get_context
from . import get_db_cursor


READABLE_PACKAGE_FIELDS = set([
    'id', 'name', 'title',
    'author', 'author_email', 'license_id', 'maintainer',
    'maintainer_email', 'notes', 'owner_org', 'type', 'url',
])
DEFAULT_PACKAGE_FIELDS = ['id', 'name', 'title']


def list_packages(size=DEFAULT_PAGE_SIZE, start=0, fields=None):
    """
    Returns a list of package names

    :param int size: pagination size
    :param int start: pagination start
    :param list fields: list of field names to return
    :return: a dict with the following keys:
        * results: a list of package names
        * total: the total amount of packages matching query
        * start, size: actual pagination arguments that were
          used (in case there is an enforced maximum limit, ..)
    """
    from ckan.model.package import package_revision_table

    if fields is None:
        fields = DEFAULT_PACKAGE_FIELDS

    if 'all' in fields:
        fields = READABLE_PACKAGE_FIELDS
    else:
        fields = filter(lambda x: x in READABLE_PACKAGE_FIELDS, fields)

    query = select([getattr(package_revision_table.c, name)
                   for name in fields])

    where_clause = and_(
        package_revision_table.c.current == True,  # noqa
        package_revision_table.c.private == False,  # noqa
        package_revision_table.c.state == 'active',
    )

    query = query.where(where_clause)

    if size is not None:
        query = query.limit(size).offset(start)
    results_page = [dict(x) for x in query.execute()]

    total_count = (select([func.count(package_revision_table.c.id)])
                   .where(where_clause)
                   .execute().first()[0])

    return {
        'results': results_page,
        'total': total_count,
        'start': start,
        'size': size,
        'fields': fields,
    }


def _package_object_from_data(data):
    """
    Get data in the format passed through the API; extract only
    the fields that should be inserted in the package/package_revision
    table..
    """
    pass


def create_package(data):
    """
    Create a package.

    We need to (pretty much):
    - validate
    - insert in postgresql
    - insert in solr
    """
    ## To insert package in PostgreSQL
    ## - need to insert in the "package" table (seems to be unused!)
    ## - need to insert in the "package_revision" table
    ## - need to insert extras in package_extra{,_revision}
    ## - need to find / create tags and associate in package_tag{,_revision}

    ## To insert package in Solr
    ## - need to connect to solr
    ## - need to transform the object in some way
    ## - need to write it to solr
    pass


def read_package(pkg_id):
    cur = get_db_cursor()
    res = cur.execute("""
    SELECT * FROM package_revision
    WHERE id=%s AND state='active' AND current=True
    """)
    return res.fetchone()


def update_package(pkg_id, update=None, delete=None):
    """
    Update package.

    We need to:
    - update in postgresql
    - validate the complete object -> if failed rollback
    - update in solr (fetch again the complete thing)
    """
    pass


def delete_package(pkg_id):
    """
    Delete package

    We need to:
    - mark as deleted in postgresql
    - delete from solr (or just update..?)
    """
    pass
