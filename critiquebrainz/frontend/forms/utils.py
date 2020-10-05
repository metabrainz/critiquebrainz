import pycountry
from babel.core import UnknownLocaleError, Locale


def get_language_name(language_code):
    try:
        return Locale(language_code).language_name
    except UnknownLocaleError:
        return pycountry.languages.get(iso639_1_code=language_code).name
