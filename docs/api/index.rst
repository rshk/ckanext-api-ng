Introduction
############

.. todo:: write this


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

Authentication is done by passing a user's API key through the ``Authorization:``
header.

  .. warning::
    Since we want to support different authentication mechanisms in the future,
    you should pass ``api-key=<your-key>`` in the ``Authorization`` header,
    not just the key as with the v3 API.

There are plans for some "better" authentication mechanism, that doesn't send
the "private" API key along with each request, but instead uses it to sign
requests (via something like `itsdangerous <http://pythonhosted.org/itsdangerous/>`_,
or HMAC signature anyways..).


Compatibility
=============

Since there are a lot of clients out there that still doesn't support all HTTP
methods / make it difficult manipulating headers, we provide some "compatibility"
arguments to "emulate" other requests via HTTP POST.

* ``?method=<NAME>`` pretend we're making a request of this type
* ``?metadata_in_body=true`` if set to ``true``, return "metadata" (such as
  pagination information) in the content body. The actual returned object will
  be moved under the ``result`` key; extra information will be added.
