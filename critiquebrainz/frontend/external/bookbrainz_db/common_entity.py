from typing import List
from brainzutils import cache
import sqlalchemy
import critiquebrainz.frontend.external.bookbrainz_db as db
from critiquebrainz.frontend.external.bookbrainz_db import DEFAULT_CACHE_EXPIRATION

MB_ARTIST_IDENTIFIER_TYPE = 2
MB_WORK_IDENTIFIER_TYPE = 3

def get_authors_for_artist(artist_mbid) -> List:
    """
    Get the author BBIDs for an artist MBID.
    Args:
        artist_mbid (str): MusicBrainz ID of the artist.
    Returns:
        List of author BBIDs.
        Empty List if no author BBIDs are found.
    """

    artist_mbid = str(artist_mbid)
    bb_author_mb_artist_key = cache.gen_key('bb_author_mb_artist', artist_mbid)
    author_bbids = cache.get(bb_author_mb_artist_key)

    # Very few artists in MB will have a BookBrainz ID, so it will be common
    # for an empty list to be cached. Hence testing for `None` rather than
    # general falsiness.
    if author_bbids is None:
        with db.bb_engine.connect() as connection:
            result = connection.execute(sqlalchemy.text("""
                SELECT ar.bbid::text AS bbid
                  FROM identifier iden
                  JOIN identifier_set__identifier idens ON idens.identifier_id = iden.id
                  JOIN author_data ad ON ad.identifier_set_id = idens.set_id
                  JOIN author_revision ar ON ar.data_id = ad.id
                  JOIN author_header ah ON ah.bbid = ar.bbid
                                       AND ah.master_revision_id = ar.id
                 WHERE iden.value = :artist_mbid
                   AND iden.type_id = :identifier_type
              GROUP BY ar.bbid
                """), {'artist_mbid': artist_mbid, 'identifier_type': MB_ARTIST_IDENTIFIER_TYPE})
            authors = result.mappings()

            author_bbids = []
            for author in authors:
                author = dict(author)
                author_bbids.append(author['bbid'])

            cache.set(bb_author_mb_artist_key, author_bbids, DEFAULT_CACHE_EXPIRATION)

    return author_bbids


def get_literary_works_for_work(work_mbid) -> List:
    """
    Get the literary work BBIDs for a work MBID.
    Args:
        work_mbid (str): MusicBrainz ID of the work.
    Returns:
        List of literary work BBIDs.
        Empty List if no literary work BBIDs are found.
    """

    work_mbid = str(work_mbid)
    bb_literary_work_mb_work_key = cache.gen_key('bb_literary_work_mb_work', work_mbid)
    work_bbids = cache.get(bb_literary_work_mb_work_key)

    # See the comment in `get_authors_for_artist` re: testing `None`.
    if work_bbids is None:
        with db.bb_engine.connect() as connection:
            result = connection.execute(sqlalchemy.text("""
                SELECT wr.bbid::text AS bbid
                  FROM identifier iden
                  JOIN identifier_set__identifier idens ON idens.identifier_id = iden.id
                  JOIN work_data wd ON wd.identifier_set_id = idens.set_id
                  JOIN work_revision wr ON wr.data_id = wd.id
                  JOIN work_header wh ON wh.bbid = wr.bbid
                                     AND wh.master_revision_id = wr.id
                 WHERE iden.value = :work_mbid
                   AND iden.type_id = :identifier_type
              GROUP BY wr.bbid
                """), {'work_mbid': work_mbid, 'identifier_type': MB_WORK_IDENTIFIER_TYPE})

            literary_works = result.mappings()
            work_bbids = []
            for literary_work in literary_works:
                literary_work = dict(literary_work)
                work_bbids.append(literary_work['bbid'])

            cache.set(bb_literary_work_mb_work_key, work_bbids, DEFAULT_CACHE_EXPIRATION)

    return work_bbids
