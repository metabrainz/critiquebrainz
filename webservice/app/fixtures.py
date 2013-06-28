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
        pass
        
    class user02:
        pass
        
    class user03:
        pass

class ReviewData(DataSet):

    class review01:
        release_group = '595eba89-8738-4e08-b8a9-c0f759655c87'
        user = UserData.user01
        text = 'Very verbose review.'
     
    class review02:
        release_group = '0596f7b0-7f5b-4fbe-a174-e176064e1c40'
        user = UserData.user01
        text = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris et nisl justo. Mauris mi massa, fermentum nec purus non, fringilla interdum sem. Integer hendrerit, nibh sit amet bibendum molestie, justo diam molestie tellus, quis blandit dui diam vel augue. Aliquam erat volutpat. Aliquam erat volutpat. Nam feugiat, justo at feugiat fermentum, tortor magna feugiat nulla, non facilisis neque turpis nec justo. Nulla lobortis risus porttitor faucibus imperdiet.'
        
    class review03:
        release_group = '595eba89-8738-4e08-b8a9-c0f759655c87'
        user = UserData.user02
        text = 'Another review concerning this album.'      
    

all_data = (UserData, ReviewData, )
