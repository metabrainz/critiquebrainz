import logging

__version__ = '0.1'

_handler = logging.StreamHandler()
_formatter = logging.Formatter("%(asctime)s %(name)-20s %(levelname)-8s %(message)s")
_handler.setFormatter(_formatter)

_logger = logging.getLogger("critiquebrainz")
# This level is set to DEBUG in critiquebrainz.frontend.create_app if Flask DEBUG=True
_logger.setLevel(logging.INFO)
_logger.addHandler(_handler)
