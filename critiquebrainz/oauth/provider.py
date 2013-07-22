from flask_oauthlib.provider import OAuth2Provider
from flask.ext.login import current_user
from datetime import datetime, timedelta
from critiquebrainz.db import db, OAuthClient, OAuthGrant, OAuthToken

class AuthProvider(OAuth2Provider):

    def _clientgetter(self, client_id):
        return OAuthClient.query.get(client_id)
    
    def _grantgetter(self, client_id, code):
        return OAuthGrant.query.filter_by(client_id=client_id, code=code).first()
    
    def _grantsetter(self, client_id, code, request, *args, **kwargs):
        # grant expires after 100 seconds
        expires = datetime.utcnow() + timedelta(seconds=100)
        grant = OAuthGrant(
            client_id=client_id,
            code=code['code'],
            redirect_uri=request.redirect_uri,
            _scopes=' '.join(request.scopes),
            user=current_user,
            expires=expires
        )
        db.session.add(grant)
        db.session.commit()
        return grant

    def _tokengetter(self, access_token=None, refresh_token=None):
        if access_token:
            return OAuthToken.query.filter_by(access_token=access_token).first()
        elif refresh_token:
            return OAuthToken.query.filter_by(refresh_token=refresh_token).first()

    def _tokensetter(self, token, request, *args, **kwargs):
        # make sure that every client has only one token connected to a user
        toks = OAuthToken.query.filter_by(client_id=request.client.client_id,
                                          user_id=request.user.id).delete()

        expires_in = token.pop('expires_in')
        expires = datetime.utcnow() + timedelta(seconds=expires_in)

        tok = OAuthToken(client_id=request.client.client_id,
            user_id=request.user.id,
            access_token=token['access_token'],
            refresh_token=token['refresh_token'],
            token_type=token['token_type'],
            _scopes=token['scope'],
            expires=expires
            )
        db.session.add(tok)
        db.session.commit()
        return tok