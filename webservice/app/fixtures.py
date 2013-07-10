from fixture import DataSet, SQLAlchemyFixture
from fixture.style import NamedDataStyle
from datetime import datetime
import models

def install(app, *args):
    engine = models.create_tables(app)
    db = SQLAlchemyFixture(env=models, style=NamedDataStyle(), engine=engine)
    data = db.data(*args)
    data.setup()
    db.dispose()

class UserData(DataSet):

    class user01:
        id = '92cbeff4-7dd4-48e9-8a0c-5daeaae0f0a8'
        
    class user02:
        id = '6603dd7f-6833-4df0-93ee-fba0a4249792'
        
    class user03:
        id = '5e6ba9d1-c7de-4be2-9d87-36dee1c009bb'

class PublicationData(DataSet):

    class publication01:
        id = 'e5364f9c-dcea-4767-8b38-c4e53c917e07'
        release_group = 'e78765b3-c84f-459e-a7bf-d6740d685c56'
        user = UserData.user01
        text = 'Very verbose publication.'
        created = datetime(2013, 06, 29, 10, 30, 20)
        last_update = None
     
    class publication02:
        id = '378555cc-78c3-4522-a79c-a73efb19adae'
        release_group = '314cffd4-daa5-3337-85e5-e54165a96113'
        user = UserData.user01
        text = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris et nisl justo. Mauris mi massa, fermentum nec purus non, fringilla interdum sem. Integer hendrerit, nibh sit amet bibendum molestie, justo diam molestie tellus, quis blandit dui diam vel augue. Aliquam erat volutpat. Aliquam erat volutpat. Nam feugiat, justo at feugiat fermentum, tortor magna feugiat nulla, non facilisis neque turpis nec justo. Nulla lobortis risus porttitor faucibus imperdiet.'
        created = datetime(2013, 06, 29, 10, 30, 20)

    class publication03:
        id = '4e11adff-6a07-4cdf-a571-e94da3a6a374'
        release_group = 'e78765b3-c84f-459e-a7bf-d6740d685c56'
        user = UserData.user02
        text = 'Another publication concerning this album.'      
        created = datetime(2013, 06, 29, 10, 30, 20)
        
class OAuthConsumerData(DataSet):

    class oauth_consumer01:
        id = 'f1debd62-aad8-43ff-9814-f1c75cad2441'
        consumer_key = 'b9481301-8adc-452a-83d2-180c8eec53fb'
        consumer_secret = 'e03fbc0e-2308-46d4-a5a2-c3e54706db9f'
        user = UserData.user01
        name = 'CritiqueBrainz'
        desc = 'A CritiqueBrainz frontend.'
        website = 'http://critiquebrainz.org/'
        callback = 'http://critiquebrainz.org/post_login'
        
all_data = (UserData, PublicationData, OAuthConsumerData, )
