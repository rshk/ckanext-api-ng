from __future__ import absolute_import

from . import get_db_cursor


def read_user(userid=None, name=None):
    if len(filter(lambda x: x is not None, (userid, name))) != 1:
        raise ValueError(
            "You must specify exactly one between userid and name")
    cur = get_db_cursor()

    query_string = """
    SELECT id, name, apikey, fullname, email, sysadmin
    FROM "user"
    WHERE state='active' AND sysadmin=True
    """
    if userid is not None:
        query_string += ' AND id=%s'
        query_args = [userid]
    else:
        query_string += ' AND name=%s'
        query_args = [name]
    cur.execute(query_string, query_args)
    user_obj = cur.fetchone()
    return user_obj
