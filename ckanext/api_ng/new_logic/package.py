"""New methods for package CRUD"""

from __future__ import absolute_import

from ckan.common import request, c
import ckan.model
from ckan.logic import check_access

from sqlalchemy import and_
from sqlalchemy.sql import select
from sqlalchemy.orm import aliased

from . import DEFAULT_PAGE_SIZE, get_context
from . import get_db_cursor


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

    cur = get_db_cursor()

    ## Get results page
    limiting = ''
    if size is not None:
        limiting = 'LIMIT {0:d} OFFSET {1:d}'.format(size, start)
    res = cur.execute("""
    SELECT "name" FROM "package_revision"
    WHERE state='active' AND current=True AND private=False
    ORDER BY name ASC
    """ + limiting)
    results_page = [r['name'] for r in cur.fetchall()]

    ## Get total count of records
    res = cur.execute("""
    SELECT count(*) AS cnt
    FROM "package_revision"
    WHERE state='active' AND current=True AND private=False
    """)
    total_count = res.fetchone()['cnt']

    return {
        'results': results_page,
        'total': total_count,
        'start': start,
        'size': size,
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
