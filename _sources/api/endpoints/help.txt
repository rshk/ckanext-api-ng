Help and documentation
######################

The ``help`` endpoint provides information about available endpoints.

Examples
========

.. code-block:: console

    % http 'http://127.0.0.1:5000/api/ng/help'


.. code-block:: http

    HTTP/1.0 200 OK
    Cache-Control: no-cache
    Content-Length: 2354
    Content-Type: application/json; charset=utf-8
    Date: Fri, 17 Jan 2014 10:01:50 GMT
    Pragma: no-cache
    Server: PasteWSGIServer/0.5 Python/2.7.3

.. code-block:: javascript

    {
        "GET /help": {
            "doc": "Return documentation about available API resources",
            "help_url": "/api/ng/help/get_help_index"
        },
        "GET /help/{id}": {
            "doc": "Get help about a given api call",
            "help_url": "/api/ng/help/get_help"
        },
        "GET /package": {
            "doc": "Return list of packages (datasets).\n\n:param start:\n:param size:",
            "help_url": "/api/ng/help/get_package_index"
        },
        "GET /package/{id}": {
            "doc": "Get a package metadata, by id",
            "help_url": "/api/ng/help/get_package"
        },
        "POST /package": {
            "doc": "Create a new dataset",
            "help_url": "/api/ng/help/post_package_index"
        },
        "PATCH /package/{id}": {
            "doc": null,
            "help_url": "/api/ng/help/patch_package"
        },
        "DELETE /package/{id}": {
            "doc": null,
            "help_url": "/api/ng/help/delete_package"
        },
	// ...
    }


Help about a given method
-------------------------

.. code-block:: console

    % http 'http://127.0.0.1:5001/api/ng/help/get_package'

.. code-block:: http

    HTTP/1.0 200 OK
    Cache-Control: no-cache
    Content-Length: 83
    Content-Type: application/json; charset=utf-8
    Date: Fri, 17 Jan 2014 10:31:34 GMT
    Pragma: no-cache
    Server: PasteWSGIServer/0.5 Python/2.7.3

.. code-block:: javascript

    {
        "doc": "Get a package metadata, by id",
        "help_url": "/api/ng/help/get_package",
        "title": "GET /package/{id}",
        // additional info can be added here
    }
