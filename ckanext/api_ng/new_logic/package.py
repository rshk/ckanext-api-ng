"""New methods for package CRUD"""

from ckan.common import request, c
import ckan.model
from ckan.logic import check_access

from sqlalchemy import and_
from sqlalchemy.sql import select
from sqlalchemy.orm import aliased

from . import DEFAULT_PAGE_SIZE, get_context


def list_packages(size=DEFAULT_PAGE_SIZE, start=0):
    """
    Returns a list of package names

    :param int size: pagination size
    :param int start: pagination start
    :return: a dict with the following keys:
        * results: a list of package names
        * total: the total amount of packages matching query
        * start, size: actual pagination arguments that were
          used (in case there is an enforced maximum limit, ..)
    """

    table = ckan.model.package_revision_table
    col = table.c.name
    query = (
        select([col])
        .where(and_(
            table.c.state == 'active',
            table.c.current == True,  # noqa
            table.c.private == False,  # noqa
            ))
        .order_by(col))

    ## Count all datasets.
    ## We need to use an alias or postgresql will complain.
    total_count = aliased(query, 'query').count().execute().first()[0]

    if size is not None:
        query = query.offset(start).limit(size)

    ## Returns the first field in each result record
    results = [r[0] for r in query.execute()]
    return {
        'results': results,
        'total': total_count,
        'start': start,
        'size': size,
    }


def create_package(data):
    """
    Create a package.

    We need to (pretty much):
    - validate
    - insert in postgresql
    - insert in solr
    """

    context = get_context()


def read_package(pkg_id):
    pass


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
