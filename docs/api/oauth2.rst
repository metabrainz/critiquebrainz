OAuth 2.0
=========

Introduction
------------

OAuth 2.0 is a protocol that lets you create applications that can request access different parts of user profiles.
This page describes how to use OAuth 2.0 when accessing a server API from a web server application.

All developers need to `register their application <https://critiquebrainz.org/profile/applications/>`_ before
getting started. A registered OAuth application is assigned a unique Client ID and Client Secret.
The Client Secret should not be shared.

Authorization
-------------

Requesting authorization
^^^^^^^^^^^^^^^^^^^^^^^^

The authorization process starts by redirecting the user to the authorization endpoint with a set of
query string parameters describing the authorization request.
The endpoint is located at ``https://critiquebrainz.org/oauth/authorize`` and is only available over HTTPS.
HTTP connections are refused.

**Parameters:**

+---------------+----------------------------------------------------------------------------------------+
| Parameter     | Description                                                                            |
+===============+========================================================================================+
| response_type | Desired grant type. Must be set to ``code``.                                           |
+---------------+----------------------------------------------------------------------------------------+
| client_id     | Client ID assigned to your application.                                                |
+---------------+----------------------------------------------------------------------------------------+
| redirect_uri  | URL where clients should be redirected after authorization. It must match exactly      |
|               | the URL you entered when registering your application.                                 |
+---------------+----------------------------------------------------------------------------------------+
| scope         | *Optional.* Comma separated set of scopes. Identifies resources that your application  |
|               | will have access to. You should request only the scopes that your application needs.   |
|               | See :ref:`oauth-scopes` for more info.                                                 |
+---------------+----------------------------------------------------------------------------------------+
| state         | *Optional.* Random string that is used to protect against cross-site request forgery   |
|               | attacks. Server roundtrips this parameter, so your application receives the same value |
|               | it sent.                                                                               |
+---------------+----------------------------------------------------------------------------------------+

**Example**::

   https://critiquebrainz.org/oauth/authorize?
      response_type=code&
      scope=review,vote&
      redirect_uri=http%3A%2F%2Fwww.example.com.com%2Fcallback&
      client_id=yDDvwAzPUnoD8imvTpVm&
      access_type=offline

Handling server response
^^^^^^^^^^^^^^^^^^^^^^^^

The response will be sent to the ``redirect_url`` specified in configuration of your application.
If user approves access request, then the response will contain authorization code and ``state``
parameter (if it was included in the request)::

   https://www.example.com/callback?state=a35Bsw1koA3pM34&code=3lUq7v15Qqm9g8YcoUT31D

If the user does not approve the request, the response will contain an error message::

   https://www.example.com/callback?state=a35Bsw1koA3pM34&error=access_denied

Access token
------------

Exchanging authorization code for an access token
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After your application receives an authorization code, it can send a *POST* request the token endpoint
located at ``https://critiquebrainz.org/ws/1/oauth/token``, to exchange the authorization code for
an access token. As before, this endpoint is only available over HTTPS and HTTP requests will be refused.
The request includes following parameters:

+---------------+----------------------------------------------------------------------------------------+
| Parameter     | Description                                                                            |
+===============+========================================================================================+
| code          | The authorization code returned from authorization request.                            |
+---------------+----------------------------------------------------------------------------------------+
| client_id     | Client ID assigned to your application.                                                |
+---------------+----------------------------------------------------------------------------------------+
| client_secret | Client secret assigned to your application.                                            |
+---------------+----------------------------------------------------------------------------------------+
| redirect_uri  | URL where response will be sent. Must match your application configuration.            |
+---------------+----------------------------------------------------------------------------------------+
| grant_type    | Must be set to ``authorization_code``.                                                 |
+---------------+----------------------------------------------------------------------------------------+

Token request might look like this::

   POST /ws/1/oauth/token HTTP/1.1
   Host: critiquebrainz.org
   Content-Type: application/x-www-form-urlencoded

   code=3lUq7v15Qqm9g8YcoUT31D&
   client_id=yDDvwAzPUnoD8imvTpVm&
   client_secret=AFjfpM7Ar1KtD0bnfV5InQ&
   redirect_uri=http%3A%2F%2Fwww.example.com%2Fcallback&
   grant_type=authorization_code

Successful response to this request will contain the following fields:

+---------------+----------------------------------------------------------------------------------------+
| Field         | Description                                                                            |
+===============+========================================================================================+
| access_token  | Access token that can be used to get data from CritiqueBrainz API                      |
+---------------+----------------------------------------------------------------------------------------+
| token_type    | Type of returned access token. Will have ``Bearer`` value.                             |
+---------------+----------------------------------------------------------------------------------------+
| expires_in    | The remaining lifetime of returned access token.                                       |
+---------------+----------------------------------------------------------------------------------------+
| refresh_token | Token that can be used to obtain new access token. See below for more info about this. |
+---------------+----------------------------------------------------------------------------------------+

Response example::

   {
     "access_token": "2YotnFZFEjr1zCsicMWpAA",
     "expires_in": 3600,
     "token_type": "Bearer",
     "refresh_token": "tGzv3JOkF0XG5Qx2TlKWIA"
   }

Refreshing an access token
^^^^^^^^^^^^^^^^^^^^^^^^^^
To obtain a new access token, your application needs to send POST request to
``https://critiquebrainz.org/ws/1/oauth/token``. The request must include the following parameters:

+---------------+----------------------------------------------------------------------------------------+
| Parameter     | Description                                                                            |
+===============+========================================================================================+
| refresh_token | The refresh token returned during the authorization code exchange.                     |
+---------------+----------------------------------------------------------------------------------------+
| client_id     | Client ID assigned to your application.                                                |
+---------------+----------------------------------------------------------------------------------------+
| client_secret | Client secret assigned to your application.                                            |
+---------------+----------------------------------------------------------------------------------------+
| redirect_uri  | URL where response will be sent. Must match your application configuration.            |
+---------------+----------------------------------------------------------------------------------------+
| grant_type    | Must be set to ``refresh_token``                                                       |
+---------------+----------------------------------------------------------------------------------------+

Request might look like this::

   POST /ws/1/oauth/token HTTP/1.1
   Host: critiquebrainz.org
   Content-Type: application/x-www-form-urlencoded

   refresh_token=tGzv3JOkF0XG5Qx2TlKWIA&
   client_id=yDDvwAzPUnoD8imvTpVm&
   client_secret=AFjfpM7Ar1KtD0bnfV5InQ&
   redirect_uri=http%3A%2F%2Fwww.example.com%2Fcallback&
   grant_type=refresh_token

As long as the user has not revoked the access granted to your application, you will receive response
that will look like this::

   {
     "access_token": "zIYanFZFEjr1zCsicMWpo6",
     "expires_in": 3600,
     "token_type": "Bearer",
     "refresh_token": "PUnoD8im10XG5QxGzv3JO1"
   }


.. _oauth-scopes:

Scopes
------

Authorization requests have a limited scope. You should request only the scopes that your application
necessarily needs. CritiqueBrainz provides the following scopes:

* ``review`` - Create and modify reviews.
* ``vote`` - Submit and delete votes on reviews.
* ``user`` - Modify profile info and delete profile.
