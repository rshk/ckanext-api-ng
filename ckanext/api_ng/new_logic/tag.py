from sqlalchemy.sql import select, insert, update, delete, and_

from ckan.model import Session
from ckan.model.tag import tag_table
from ckan.model.vocabulary import vocabulary_table


## Tags
##------------------------------------------------------------

def list_tags():
    query = select([tag_table])
    return [dict(row) for row in query.execute()]


def read_tag(tag_id):
    query = (
        select([tag_table])
        .where(tag_table.c.id == tag_id))
    res = query.execute().first()
    if res is not None:
        return dict(res)


def read_tag_by_name(name):
    query = (
        select([tag_table])
        .where(tag_table.c.name == name))
    res = query.execute().first()
    if res is not None:
        return dict(res)


def create_tag(obj):
    query = (
        insert([tag_table])
        .values(**obj)
        .returning(tag_table.c.id))
    return query.execute().first()[0]


def update_tag(id, obj):
    query = (
        update([tag_table])
        .where(tag_table.c.id == id)
        .values(**obj)
        .returning(tag_table.c.id))
    return query.execute().first()[0]


def delete_tag(id):
    query = (
        delete([tag_table])
        .where(tag_table.c.id == id))
    query.execute()


def ensure_tag(name, vocabulary=None):
    """
    Make sure a tag with this name (and vocabulary) exists.
    :return: the tag id
    """
    obj = {'name': name}
    where_clause = tag_table.c.name == name

    if vocabulary is not None:
        ## Add vocabulary to filter / new object
        vocabulary_id = ensure_vocabulary(vocabulary)
        obj['vocabulary_id'] = vocabulary_id
        where_clause = and_(
            where_clause, tag_table.c.vocabulary_id == vocabulary_id)

    query = select([tag_table]).where(where_clause)
    tag_obj = query.execute().first()

    if tag_obj is not None:
        ## We already have the tag!
        return tag_obj['id']

    ## Create tag, return id
    return create_tag(obj)


## Vocabularies
##------------------------------------------------------------

def list_vocabularies():
    query = select([vocabulary_table])
    return [dict(row) for row in query.execute()]


def read_vocabulary(vocabulary_id):
    """Get a vocabulary, by id"""
    query = (
        select([vocabulary_table])
        .where(vocabulary_table.c.id == vocabulary_id))
    res = query.execute().first()
    if res is not None:
        return dict(res)


def read_vocabulary_by_name(name):
    """Get a vocabulary, by name"""
    res = (
        select([vocabulary_table])
        .where(vocabulary_table.c.name == name)
        .execute().first())
    if res is not None:
        return dict(res)


def create_vocabulary(obj):
    """
    Create a vocabulary

    :param dict obj: values for the vocabulary fields
    """
    query = (
        insert(vocabulary_table)
        .values(**obj)
        .returning(vocabulary_table.c.id))
    return query.execute().first()[0]


def update_vocabulary(id, obj):
    """
    :param id: id of the vocabulary to update
    :param obj: keys to be updated on the vocabulary
    """
    query = (
        update(vocabulary_table)
        .where(vocabulary_table.c.id == id)
        .values(**obj)
        .returning(vocabulary_table.c.id))
    return query.execute().first()[0]


def delete_vocabulary(id, cascade=True):
    """
    Delete a vocabulary, by id

    :param id: vocabulary id
    :param cascade: if True, delete all tags in this vocabulary first
    """
    conn = Session.connection()
    with conn.begin():
        if cascade:
            query = delete(tag_table).where(tag_table.c.vocabulary_id == id)
            query.execute()
        query = delete(vocabulary_table).where(vocabulary_table.c.id == id)


def ensure_vocabulary(name):
    """
    Make sure a vocabulary with this name exists.

    :param name: vocabulary name
    :return: vocabulary id
    """
    vocab = read_vocabulary_by_name(name)
    if vocab is None:
        return create_vocabulary(name)
    return vocab['id']
