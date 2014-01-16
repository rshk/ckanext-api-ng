Introduction
############

The API is somehow in between a RESTful and a RPC-like API, mainly
to provide compatibility for clients not supporting 100% of the HTTP.


Serialization format(s)
=======================

Right now the only format "spoken" by the API is json.
There are plans for:

* full json-ld suppport
* rdf (xml, turtle, n3, ..)
* (maybe) msgpack, protobuf, ...


Pagination
==========

* All the pagination is handled using the ``start`` and ``size`` query arguments.
* Pagination links are returned in the ``Link:`` header
* **todo:** we need to figure out some way to pass total count back.


Sorting
=======

* Sorting is controlled by the ``order_by`` query argument.
* The format is ``<field>[,<direction>]`` where direction can be one of ``ASC``
  or ``DESC``. If none is specified, ``ASC`` is assumed.
* Can be used multiple times to add more than one sorting column
* Example: ``GET /package?order_by=author,ASC&order_by=date,DESC``


Authentication
==============

Right now, the only supported authentication method is ``Basic`` http authentication,
on username + api key.

While this kind of authentication is supported by most clients, it can be recreated
by setting the ``Authorization:`` header to ``Basic {value}`` where ``{value}`` is
the base-64 encoded representation of ``username:apikey``.

There are plans for some "better" authentication mechanism, that doesn't send
the "private" API key along with each request, but instead uses it to sign
requests (via something like `itsdangerous <http://pythonhosted.org/itsdangerous/>`_,
or HMAC signature anyways..).


Fields selection
================

Most "index" pages allow fields selection. This is done by specifying a comma-separated
list of field names in the ``?fields=`` argument.

Special cases
-------------

* The ``link`` field is "virtual": if requested for, it will be the (relative) link
  to the object itself, where applicable.
* If just **one** field is requested, and it is one of ``id``, ``name`` or ``link``,
  just a list of that field values will be returned, instead of a list of dictionaries.
* You can specify ``all`` to mean "all fields". This can be of course combined with
  ``link``, to get links in addition to all fields.


RDF and Json-LD
===============

This part is Work in progress, and decisions must be made about it.


Compatibility
=============

Since there are a lot of clients out there that still doesn't support all HTTP
methods / make it difficult manipulating headers, we provide some "compatibility"
arguments to "emulate" other requests via HTTP POST.

* ``?method=<NAME>`` pretend we're making a request of this type
* ``?metadata_in_body=true`` if set to ``true``, return "metadata" (such as
  pagination information) in the content body. The actual returned object will
  be moved under the ``result`` key; extra information will be added.
