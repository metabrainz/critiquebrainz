Server Web API
==============

CritiqueBrainz provides various endpoints that can be used to interact with the
data. Web API uses JSON format.

**Root URL**: ``https://critiquebrainz.org/ws/1``

Reference
---------

Below you will find description of all available endpoints.

Reviews
^^^^^^^

.. autoflask:: critiquebrainz.ws:create_app_sphinx()
   :blueprints: ws_review
   :include-empty-docstring:
   :undoc-static:

Users
^^^^^

.. autoflask:: critiquebrainz.ws:create_app_sphinx()
   :blueprints: ws_user
   :include-empty-docstring:
   :undoc-static:

OAuth
^^^^^

.. autoflask:: critiquebrainz.ws:create_app_sphinx()
   :blueprints: ws_oauth
   :include-empty-docstring:
   :undoc-static:
