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

class ReviewData(DataSet):

    class review01:
        id = 'e5364f9c-dcea-4767-8b38-c4e53c917e07'
        release_group = '595eba89-8738-4e08-b8a9-c0f759655c87'
        user = UserData.user01
        text = 'Very verbose review.'
        created = datetime(2013, 06, 29, 10, 30, 20)
        last_update = None
     
    class review02:
        id = '378555cc-78c3-4522-a79c-a73efb19adae'
        release_group = '0596f7b0-7f5b-4fbe-a174-e176064e1c40'
        user = UserData.user01
        text = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris et nisl justo. Mauris mi massa, fermentum nec purus non, fringilla interdum sem. Integer hendrerit, nibh sit amet bibendum molestie, justo diam molestie tellus, quis blandit dui diam vel augue. Aliquam erat volutpat. Aliquam erat volutpat. Nam feugiat, justo at feugiat fermentum, tortor magna feugiat nulla, non facilisis neque turpis nec justo. Nulla lobortis risus porttitor faucibus imperdiet.'
        created = datetime(2013, 06, 29, 10, 30, 20)

    class review03:
        id = '4e11adff-6a07-4cdf-a571-e94da3a6a374'
        release_group = '595eba89-8738-4e08-b8a9-c0f759655c87'
        user = UserData.user02
        text = 'Another review concerning this album.'      
        created = datetime(2013, 06, 29, 10, 30, 20)

all_data = (UserData, ReviewData, )
