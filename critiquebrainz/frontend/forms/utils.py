import pycountry
from babel.core import UnknownLocaleError, Locale


def get_language_name(language_code):
    try:
        return Locale(language_code).language_name
    except UnknownLocaleError:
        return pycountry.languages.get(alpha_2=language_code).name
