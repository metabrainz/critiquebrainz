API Documentation
=================

This page describes all resources available via CririqueBrainz Server API. It uses JSON format.

**Root URL**: ``http://critiquebrainz.org/ws/1``

`CritiqueBrainz client is build on top of this API, so you can use it as an example.`

Reviews
-------
.. autoflask:: server.critiquebrainz:app
   :blueprints: review
   :include-empty-docstring:
   :undoc-static:

Users
-----
.. autoflask:: server.critiquebrainz:app
   :blueprints: user
   :include-empty-docstring:
   :undoc-static:

OAuth
-----
.. autoflask:: server.critiquebrainz:app
   :blueprints: oauth
   :include-empty-docstring:
   :undoc-static:

Login
-----
.. autoflask:: server.critiquebrainz:app
   :blueprints: login
   :include-empty-docstring:
   :undoc-static:

Client
------
.. autoflask:: server.critiquebrainz:app
   :blueprints: client
   :include-empty-docstring:
   :undoc-static: