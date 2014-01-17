Endpoints
#########

All the API are nested under a prefix, usually ``/api/ng/``.

``package``
===========

Resource for packages management.

* Supports pagination
* Supports field selection: id, name, title, author, author_email, license_id,
  maintainer, maintainer_email, notes, owner_org, type, url
* Supports linking

Methods
-------

* ``GET /package`` -> list packages
* ``GET /package/<id>`` -> get the specified package
* WIP ``POST /package`` -> create new package
* WIP ``PUT /package/<id>`` -> full update of a packa
* WIP ``PATCH /package/<id>`` -> partial update of a package
* WIP ``DELETE /package/<id>`` -> delete a package

Relationships
-------------

* WIP ``GET /package/<id>/resources`` -> list package resources


``resource``
============

Methods
-------

* WIP ``GET /resource/<id>`` -> get the specified resource
* WIP ``POST /resource`` -> create new resource
* WIP ``PUT /resource/<id>`` -> full update of a packa
* WIP ``PATCH /resource/<id>`` -> partial update of a resource
* WIP ``DELETE /resource/<id>`` -> delete a resource


``vocabulary``
==============

Manage tag vocabularies.

* WIP ``GET /vocabulary`` -> list vocabularies
* WIP ``POST /vocabulary`` -> create vocabulary
* WIP ``DELETE /vocabulary`` -> delete vocabulary
* WIP ``GET /vocabulary/<id>`` -> list tags in this vocabulary
* WIP ``POST /vocabulary/<id>`` -> add tag in this vocabulary
* WIP ``DELETE /vocabulary/<id>/<tag_id>`` -> delete tag from this vocabulary
