from brainzutils import cache
from critiquebrainz.test_config import REDIS_HOST, REDIS_PORT, REDIS_NAMESPACE


def setup_cache():
    cache.init(
        host=REDIS_HOST,
        port=REDIS_PORT,
        namespace=REDIS_NAMESPACE,
    )
