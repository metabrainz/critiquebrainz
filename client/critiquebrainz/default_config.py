# -*- coding: utf-8 -*-
# DEFAULT CONFIGURATION

# CritiqueBrainz server
CRITIQUEBRAINZ_BASE_URI = "http://127.0.0.1:5000/"

# Server with Spotify mappings
MBSPOTIFY_BASE_URI = "http://127.0.0.1:8080/"

MEMCACHED_SERVERS = ["127.0.0.1:11211"]
MEMCACHED_NAMESPACE = "CB_CLIENT"

# Mail server
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USERNAME = None
MAIL_PASSWORD = None
MAIL_FROM_ADDR = "no-reply@critiquebrainz.org"

# Logging
LOG_FILE = "client.log"
LOG_EMAIL_TOPIC = "CritiqueBrainz Client Failure"

# Internationalization and localization
LANGUAGES = {
    # Valid language codes can be obtained from Transifex.
    # Example:
    # '<valid langauage code>: u'<Language name>',

    'en': u'English',
    'de': u'Deutsch',
    'es': u'Español',
    'nl': u'Dutch',
    'ru': u'Русский',
    'el': u'Greek',
    'hr': u'Hrvatski',
    'eo': u'Esperanto',
}
