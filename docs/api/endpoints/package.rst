Packages and resources
######################

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


Examples
========

Getting list of datasets
------------------------

.. code-block:: console

    % http 'http://127.0.0.1:5001/api/ng/package?size=5'

.. code-block:: http

    HTTP/1.0 200 OK
    Cache-Control: no-cache
    Content-Length: 593
    Content-Type: application/json; charset=utf-8
    Date: Fri, 17 Jan 2014 10:35:25 GMT
    Link: </api/ng/package?start=0&fields=id%2Cname%2Ctitle&size=5>; rel=first,
        </api/ng/package?start=580&fields=id%2Cname%2Ctitle&size=5>; rel=last,
        </api/ng/package?start=5&fields=id%2Cname%2Ctitle&size=5>; rel=next
    Pragma: no-cache
    Server: PasteWSGIServer/0.5 Python/2.7.3
    x-page-size: 5
    x-page-start: 0
    x-result-total: 583

.. code-block:: javascript

    [
        {
            "id": "02d09ad1-34d6-462f-932b-ee8a9ede9993",
            "name": "example-dataset-0",
            "title": "Example dataset #0"
        },
        {
            "id": "771e7b45-58c9-4126-9688-f01e1a2f3d80",
            "name": "example-dataset-1",
            "title": "Example dataset #1"
        },
        {
            "id": "3074389b-34ee-4bb2-886c-fec45bd00d76",
            "name": "example-dataset-2",
            "title": "Example dataset #2"
        },
        {
            "id": "7027c0a1-dc9e-4ec6-b846-0c5cc622a5a0",
            "name": "example-dataset-3",
            "title": "Example dataset #3"
        },
        {
            "id": "9aecb103-f286-45ec-9bbc-7b1dd0926b59",
            "name": "example-dataset-4",
            "title": "Example dataset #4"
        }
    ]

Getting links to datasets
-------------------------

.. code-block:: console

    % http 'http://127.0.0.1:5001/api/ng/package?fields=link'

.. code-block:: http

    HTTP/1.0 200 OK
    Cache-Control: no-cache
    Content-Length: 1192
    Content-Type: application/json; charset=utf-8
    Date: Fri, 17 Jan 2014 10:41:19 GMT
    Link: </api/ng/package?start=0&fields=id&size=20>; rel=first, </api/ng/package?start=580&fields=id&size=20>; rel=last, </api/ng/package?start=20&fields=id&size=20>; rel=next
    Pragma: no-cache
    Server: PasteWSGIServer/0.5 Python/2.7.3
    x-page-size: 20
    x-page-start: 0
    x-result-total: 583

.. code-block:: javascript

    [
        "/api/ng/package/02d09ad1-34d6-462f-932b-ee8a9ede9993",
        "/api/ng/package/771e7b45-58c9-4126-9688-f01e1a2f3d80",
        "/api/ng/package/3074389b-34ee-4bb2-886c-fec45bd00d76",
        "/api/ng/package/7027c0a1-dc9e-4ec6-b846-0c5cc622a5a0",
        "/api/ng/package/9aecb103-f286-45ec-9bbc-7b1dd0926b59",
        "/api/ng/package/7b513174-f80a-442b-a7ae-c63cbcb9c6cb",
        "/api/ng/package/d9d59e1b-a67b-4ae1-8086-2b9088240fd3",
        "/api/ng/package/7e84ae8b-9457-44fe-a68f-594a7cde8525",
        "/api/ng/package/467928ee-4446-44d7-bbb4-0f0484f0ca7d",
        "/api/ng/package/c7e09ed3-b948-452f-a3d7-922fa34359d2",
        "/api/ng/package/5d8e2dfa-0eb4-41ea-a1fb-f032550b0533",
        "/api/ng/package/d9239daf-6ea0-4d90-8271-9eafc1235490",
        "/api/ng/package/7c2d1fa0-c0cb-4f52-970a-ac57c720f57a",
        "/api/ng/package/f0d5765f-7170-4af0-9819-72a078af1811",
        "/api/ng/package/06b70d1d-79db-4bc1-a09d-13a35244f4b9",
        "/api/ng/package/0b98e9a5-0077-470c-b4f4-88bb1ed32d06",
        "/api/ng/package/515a211a-1e96-40b0-a2ff-73cd53ec6ac3",
        "/api/ng/package/87aa0dc9-459d-418d-a738-b128a136fe35",
        "/api/ng/package/c91919b4-48bb-455a-8715-c6fd06a66414",
        "/api/ng/package/cf080127-6696-4914-a0f4-fe69277b9a14",
    ]
