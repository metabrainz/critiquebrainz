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

class UserData(object):

    user01 = User(display_name=u'user01', 
                  twitter_id=u'1577950832')
                  
    user02 = User(display_name=u'user02',
                  musicbrainz_id=u'mjjc')
            
class PublicationData(object):

    publication01 = Publication(
        id = u'e5364f9c-dcea-4767-8b38-c4e53c917e07',
        release_group = u'e78765b3-c84f-459e-a7bf-d6740d685c56',
        user = UserData.user01,
        text = u'Very verbose publication.',
        created = datetime(2013, 06, 29, 10, 30, 20))
     
    publication02 = Publication(
        id = u'378555cc-78c3-4522-a79c-a73efb19adae',
        release_group = u'314cffd4-daa5-3337-85e5-e54165a96113',
        user = UserData.user01,
        text = u'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris et nisl justo. Mauris mi massa, fermentum nec purus non, fringilla interdum sem. Integer hendrerit, nibh sit amet bibendum molestie, justo diam molestie tellus, quis blandit dui diam vel augue. Aliquam erat volutpat. Aliquam erat volutpat. Nam feugiat, justo at feugiat fermentum, tortor magna feugiat nulla, non facilisis neque turpis nec justo. Nulla lobortis risus porttitor faucibus imperdiet.',
        created = datetime(2013, 06, 29, 10, 30, 20))
        
class OAuthClientData(object):

    oauth_client01 = OAuthClient(
        client_id = u'b9481301-8adc-452a-83d2-180c8eec53fb',
        client_secret = u'e03fbc0e-2308-46d4-a5a2-c3e54706db9f',
        user = UserData.user01,
        name = u'CritiqueBrainz',
        desc = u'A CritiqueBrainz frontend.',
        website = u'http://critiquebrainz.org',
        redirect_uri = u'http://127.0.0.1:5001/login/post',
        scopes = u'user publication authorization')
        
all_data = (UserData, PublicationData, OAuthClientData, )
