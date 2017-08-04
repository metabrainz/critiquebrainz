from brainzutils import cache


REDIS_HOST = 'critiquebrainz_redis'
REDIS_PORT = 6379
REDIS_NAMESPACE = 'CB'


def setup_cache():
    cache.init(
        host=REDIS_HOST,
        port=REDIS_PORT,
        namespace=REDIS_NAMESPACE,
    )
