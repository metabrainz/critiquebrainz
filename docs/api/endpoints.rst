Endpoint reference
==================

CritiqueBrainz provides various endpoints that can be used to interact with the
data. Web API uses JSON format.

**Root URL**: ``https://critiquebrainz.org/ws/1``

Below you will find description of all available endpoints.

Reviews
^^^^^^^

.. autoflask:: critiquebrainz.ws:create_app_sphinx()
   :blueprints: ws_review
   :include-empty-docstring:
   :undoc-static:

.. autoflask:: critiquebrainz.ws:create_app_sphinx()
   :blueprints: ws_review_bulk
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

See :doc:`OAuth documentation <oauth2>` for more info.

.. autoflask:: critiquebrainz.ws:create_app_sphinx()
   :blueprints: ws_oauth
   :include-empty-docstring:
   :undoc-static:

Constants
^^^^^^^^^

Constants that are relevant to using the API:

.. autodata:: critiquebrainz.db.review.ENTITY_TYPES
