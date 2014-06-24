from db import *


def install(app, *args):
    db.init_app(app)
    create_tables(app)
    for arg in args:
        for key, entity in arg.__dict__.iteritems():
            if not key.startswith("__"):
                try:
                    db.session.add(entity)
                    db.session.flush()
                except:
                    print 'failed to add %s' % key
                    db.session.rollback()
                else:
                    print 'added %s' % key
    db.session.commit()


class OAuthClientData(object):
    # TODO: Fix redirect_uri
    oauth_client01 = OAuthClient(
        client_id=u'b9481301-8adc-452a-83d2-180c8eec53fb',
        client_secret=u'e03fbc0e-2308-46d4-a5a2-c3e54706db9f',
        name=u'CritiqueBrainz',
        desc=u'A CritiqueBrainz frontend.',
        website=u'http://critiquebrainz.org',
        redirect_uri=u'http://127.0.0.1:5001/login/post')


class LicenseData(object):
    cc_by_sa_3 = License(
        id=u"CC BY-SA 3.0",
        full_name=u"Creative Commons Attribution-ShareAlike 3.0 Unported",
        info_url=u"https://creativecommons.org/licenses/by-sa/3.0/")
    cc_by_nc_sa_3 = License(
        id=u"CC BY-NC-SA 3.0",
        full_name=u"Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported",
        info_url=u"https://creativecommons.org/licenses/by-nc-sa/3.0/")


all_data = (OAuthClientData, LicenseData, )
