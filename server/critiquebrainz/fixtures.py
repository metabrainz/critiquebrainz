from db import *
from datetime import datetime

def install(app, *args):
    db.init_app(app)
    engine = create_tables(app)
    for arg in args:
        for key, entity in arg.__dict__.iteritems():
            if not key.startswith("__"):
                try:
                    db.session.add(entity)
                    db.session.flush()
                except:
                    print 'failed %s' % key
                    db.session.rollback()
                else:
                    print 'added %s' % key
    db.session.commit()

class OAuthClientData(object):

    oauth_client01 = OAuthClient(
        client_id = u'b9481301-8adc-452a-83d2-180c8eec53fb',
        client_secret = u'e03fbc0e-2308-46d4-a5a2-c3e54706db9f',
        name = u'CritiqueBrainz',
        desc = u'A CritiqueBrainz frontend.',
        website = u'http://critiquebrainz.org',
        redirect_uri = u'http://127.0.0.1:5001/login/post',
        scopes = u'user review authorization rate client')
        
all_data = (OAuthClientData, )
