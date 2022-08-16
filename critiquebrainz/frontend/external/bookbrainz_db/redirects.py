import uuid
from brainzutils import cache
import sqlalchemy
import critiquebrainz.frontend.external.bookbrainz_db as db
from critiquebrainz.frontend.external.bookbrainz_db import DEFAULT_CACHE_EXPIRATION


def get_redirected_bbid(bbid: uuid.UUID) -> str:
    """
    Get the redirected BBID for a given BBID.
    Args:
        bbid: The BBID to get the redirected BBID for.
    Returns:
        The redirected BBID.
    Returns None if the BBID is not redirected.
    """
    bb_redirect_key = cache.gen_key('bb_redirects', bbid)
    results = cache.get(bb_redirect_key)

    if not results:
        with db.bb_engine.connect() as connection:
            result = connection.execute(sqlalchemy.text("""
                WITH RECURSIVE redirects AS (
                        SELECT source_bbid, target_bbid
                        FROM entity_redirect
                        WHERE source_bbid = :bbid
                    UNION 
                        SELECT er.source_bbid, er.target_bbid
                        FROM entity_redirect er
                    INNER JOIN redirects rd 
                            ON rd.target_bbid = er.source_bbid
                        )
                SELECT target_bbid::text
                FROM redirects
            """), {'bbid': bbid})

            redirect_bbids = result.fetchall()

            results = []
            for redirect_bbid in redirect_bbids:
                redirect_bbids = dict(redirect_bbid)
                results.append(redirect_bbid['target_bbid'])

            cache.set(bb_redirect_key, results, DEFAULT_CACHE_EXPIRATION)

    if results:
        return results[-1]
    else:
        return None
