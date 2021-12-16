.. image:: https://img.shields.io/badge/License-MIT-green.svg
    :alt: screenshot-py license
    :target: https://opensource.org/licenses/MIT

.. image:: https://img.shields.io/pypi/v/screenshot-api.svg
    :alt: screenshot-py release
    :target: https://pypi.org/project/screenshot-api

.. image:: https://github.com/whois-api-llc/screenshot-py/workflows/Build/badge.svg
    :alt: screenshot-py build
    :target: https://github.com/whois-api-llc/screenshot-py/actions

========
Overview
========

The client library for
`Screenshot API <https://website-screenshot.whoisxmlapi.com/>`_
in Python language.

The minimum Python version is 3.6.

Installation
============

.. code-block:: shell

    pip install screenshot-api

Examples
========

Full API documentation available `here <https://website-screenshot.whoisxmlapi.com/api/documentation/making-requests>`_

Create a new client
-------------------

.. code-block:: python

    from screenshotapi import *

    client = Client('Your API key')

Capture screenshots
-------------------

.. code-block:: python

    client.get(filename='screen.jpg',url='example.com')

Extras
-------------------

.. code-block:: python

    cookies = {
        'name1': 'value1',
        'name2': 'value2'
    }

    # Pass cookies, emulate mobile device, disable JS, wait for network idle
    # event, output API errors in XML, capture PDF screenshot in full page
    # mode and get image data in base64.
    response = client.get_raw(
        url='example.com',
        type=ImageFormat.PDF,
        mode=Client.SLOW_MODE,
        full_page=True,
        mobile=True,
        output_format=Client.XML_FORMAT,
        image_output_format=Client.BASE64_FORMAT,
        no_js=True,
        cookies=cookies
    )

