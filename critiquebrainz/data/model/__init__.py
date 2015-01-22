# This value should be incremented after any schema changes!
__version__ = 3

# All models must be imported there:
from critiquebrainz.data.model.review import Review
from critiquebrainz.data.model.revision import Revision
from critiquebrainz.data.model.user import User
from critiquebrainz.data.model.license import License
from critiquebrainz.data.model.vote import Vote
from critiquebrainz.data.model.spam_report import SpamReport
from critiquebrainz.data.model.oauth_client import OAuthClient
from critiquebrainz.data.model.oauth_grant import OAuthGrant
from critiquebrainz.data.model.oauth_token import OAuthToken
