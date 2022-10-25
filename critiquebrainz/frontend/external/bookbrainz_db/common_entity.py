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

    if not author_bbids:
        with db.bb_engine.connect() as connection:
            result = connection.execute(sqlalchemy.text("""
                SELECT bbid::text
                  FROM author
             LEFT JOIN identifier_set__identifier idens ON idens.set_id = author.identifier_set_id
             LEFT JOIN identifier iden ON idens.identifier_id = iden.id
                 WHERE iden.value = :artist_mbid
                   AND iden.type_id = :identifier_type
                   AND master = 't'
                   AND author.data_id IS NOT NULL
              GROUP BY bbid
                """), {'artist_mbid': artist_mbid, 'identifier_type': MB_ARTIST_IDENTIFIER_TYPE})
            authors = result.mappings()

            author_bbids = []
            for author in authors:
                author = dict(author)
                author_bbids.append(author['bbid'])

            cache.set(bb_author_mb_artist_key, author_bbids, DEFAULT_CACHE_EXPIRATION)

    if not author_bbids:
        return []
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

    if not work_bbids:
        with db.bb_engine.connect() as connection:
            result = connection.execute(sqlalchemy.text("""
                SELECT bbid::text
                  FROM work
             LEFT JOIN identifier_set__identifier idens ON idens.set_id = work.identifier_set_id
             LEFT JOIN identifier iden ON idens.identifier_id = iden.id
                 WHERE iden.value = :work_mbid
                   AND iden.type_id = :identifier_type
                   AND master = 't'
                   AND work.data_id IS NOT NULL
              GROUP BY bbid
                """), {'work_mbid': work_mbid, 'identifier_type': MB_WORK_IDENTIFIER_TYPE})

            literary_works = result.mappings()
            work_bbids = []
            for literary_work in literary_works:
                literary_work = dict(literary_work)
                work_bbids.append(literary_work['bbid'])

            cache.set(bb_literary_work_mb_work_key, work_bbids, DEFAULT_CACHE_EXPIRATION)

    if not work_bbids:
        return []

    return work_bbids
