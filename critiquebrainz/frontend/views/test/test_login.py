from urllib.parse import urlparse, parse_qs

import requests_mock
import sqlalchemy
from flask import url_for

import critiquebrainz.db.users as db_users
from critiquebrainz import db
from critiquebrainz.frontend.testing import FrontendTestCase


class LoginViewsTestCase(FrontendTestCase):

    def test_login_page(self):
        response = self.client.get("/login/")
        self.assert200(response)

    @requests_mock.Mocker()
    def test_login_oauth(self, mock_requests):
        """ Tests that creating a new user, update MB username and login to CB updates MB username in CB db """
        row_id = 1111

        mock_requests.post("https://musicbrainz.org/oauth2/token", json={
          "access_token": "UF7GvG2pl70jTogIwOhD32BhI_aIevPF",
          "expires_in": 3600,
          "token_type": "Bearer",
          "refresh_token": "GjSCBBjp4fnbE0AKo3uFu9qq9K2fFm4u"
        })

        mock_requests.get("https://musicbrainz.org/oauth2/userinfo", json={
            "sub": "old-user-name",
            "metabrainz_user_id": row_id
        })

        response = self.client.get(url_for("login.musicbrainz"))
        params = parse_qs(urlparse(response.location).query)
        response = self.client.get(
            url_for("login.musicbrainz_post", code="foobar", state=params["state"][0]),
            follow_redirects=True
        )
        self.assert200(response)
        user = db_users.get_by_mb_row_id(row_id)
        self.assertEqual(user["musicbrainz_username"], "old-user-name")
        self.assertEqual(user["display_name"], "old-user-name")

        self.client.get(url_for("login.logout"))

        # change MB username without changing display name, musicbrainz id in database should update
        mock_requests.get("https://musicbrainz.org/oauth2/userinfo", json={
            "sub": "new-user-name",
            "metabrainz_user_id": row_id
        })

        response = self.client.get(url_for("login.musicbrainz"))
        params = parse_qs(urlparse(response.location).query)
        response = self.client.get(
            url_for("login.musicbrainz_post", code="foobar", state=params["state"][0]),
            follow_redirects=True
        )
        self.assert200(response)
        user = db_users.get_by_mb_row_id(row_id)
        self.assertEqual(user["musicbrainz_username"], "new-user-name")
        self.assertEqual(user["display_name"], "new-user-name")

        self.client.get(url_for("login.logout"))

        # change display name to something else, this time display name should not be updated
        db_users.update(user["id"], {"display_name": "custom-display-name"})

        # change MB username, musicbrainz id in database should not update because display name is different
        mock_requests.get("https://musicbrainz.org/oauth2/userinfo", json={
            "sub": "another-new-user-name",
            "metabrainz_user_id": row_id
        })

        response = self.client.get(url_for("login.musicbrainz"))
        params = parse_qs(urlparse(response.location).query)
        response = self.client.get(
            url_for("login.musicbrainz_post", code="foobar", state=params["state"][0]),
            follow_redirects=True
        )
        self.assert200(response)
        user = db_users.get_by_mb_row_id(row_id)
        self.assertEqual(user["musicbrainz_username"], "another-new-user-name")
        self.assertEqual(user["display_name"], "custom-display-name")
