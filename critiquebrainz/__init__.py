__version__ = '0.1'

import logging

_logger = logging.getLogger('critiquebrainz')
_logger.setLevel(logging.DEBUG)
_logger.addHandler(logging.StreamHandler())
