Server Web API
==============

CritiqueBrainz server provides web service that can be used to interact with data. It uses JSON format.

**Root URL**: ``https://critiquebrainz.org/ws/1``

Reference
---------

Reviews
^^^^^^^

.. autoflask:: critiquebrainz:create_app()
   :blueprints: ws_review
   :include-empty-docstring:
   :undoc-static:

Users
^^^^^

.. autoflask:: critiquebrainz:create_app()
   :blueprints: ws_user
   :include-empty-docstring:
   :undoc-static:

OAuth
^^^^^

.. autoflask:: critiquebrainz:create_app()
   :blueprints: ws_oauth
   :include-empty-docstring:
   :undoc-static:
