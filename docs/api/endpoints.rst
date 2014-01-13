Endpoints
#########

All the API are nested under a prefix, usually ``/api/ng/``.

``package``
===========

Resource for packages management

* ``GET /package`` -> list packages
* ``GET /package/<id>`` -> get the specified package
* ``POST /package`` -> create new package
* ``PUT /package/<id>`` -> full update of a packa
* ``PATCH /package/<id>`` -> partial update of a package
* ``DELETE /package/<id>`` -> delete a package

relationships
-------------

* ``GET /package/<id>/resources`` -> list package resources


``related``
===========

"Related" objects, such as applications.

* ``GET /related`` -> list "related objects"

  * ``?package_id=<id>`` -> filter on package id
  * ``?type=<id>`` -> only return related objects of this type


``group``
=========

Return information about groups.

* ``GET /group`` -> list groups
* ``GET /group/<id>`` -> get the specified group
