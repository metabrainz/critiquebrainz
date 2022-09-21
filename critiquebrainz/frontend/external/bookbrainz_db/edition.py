import uuid
from brainzutils import cache
from typing import List
import sqlalchemy
import critiquebrainz.frontend.external.bookbrainz_db as db
from critiquebrainz.frontend.external.bookbrainz_db import DEFAULT_CACHE_EXPIRATION


def get_edition_by_bbid(bbid: str) -> dict:
    """
    Get info related to an edition using its BookBrainz ID.
    Args:
        bbid : BBID of the edition.
    Returns:
        A dictionary containing the basic information related to the edition.
        It includes the following keys:
            - bbid: BookBrainz ID of the edition.
            - name: Name of the edition.
            - sort_name: Sort name of the edition.
            - disambiguation: Disambiguation of the edition.
            - author_credits: A list of dictionaries containing the basic information on the author credits.

        Returns an empty dictionary if the edition is not found.

    """
    edition = fetch_multiple_editions([bbid])
    if not edition:
        return {}
    return edition[bbid]


def fetch_multiple_editions(bbids: List[str]) -> dict:
    """
    Get info related to multiple editions using their BookBrainz IDs. 
    Args:
        bbids (list): List of BBID of editions.
    Returns:
        A dictionary containing info of multiple editions keyed by their BBID.
    """
    if bbids == []:
        return {}

    bbids = [str(uuid.UUID(bbid)) for bbid in bbids]

    bb_edition_key = cache.gen_key('edition', bbids)
    results = cache.get(bb_edition_key)
    if not results:
        with db.bb_engine.connect() as connection:
            result = connection.execute(sqlalchemy.text("""
                SELECT 
                    bbid::text,
                    edition.name,
                    sort_name,
                    disambiguation,
                    identifier_set_id,
                    relationship_set_id,
                    edition_format.label as format,
                    COALESCE( json_agg( acn ORDER BY "position" ASC )
                              FILTER (WHERE acn IS NOT NULL),
                              '[]'
                            ) as author_credits,
                    COALESCE( json_agg(mbl.name)
                              FILTER (WHERE mbl IS NOT NULL),
                              '[]'
                            ) as languages
               FROM edition 
          LEFT JOIN author_credit_name acn ON acn.author_credit_id = edition.author_credit_id
          LEFT JOIN edition_format ON edition_format.id = edition.format_id
          LEFT JOIN bookbrainz.language_set__language lsl ON lsl.set_id = edition.language_set_id
          LEFT JOIN musicbrainz.language mbl on mbl.id = lsl.language_id
              WHERE bbid in :bbids
                AND master = 't'
           GROUP BY bbid,
                    edition.name,
                    sort_name,
                    disambiguation,
                    identifier_set_id,
                    relationship_set_id,
                    format
                """), {'bbids': tuple(bbids)})

            editions = result.fetchall()
            results = {}
            for edition in editions:
                edition = dict(edition)
                results[edition['bbid']] = edition

            cache.set(bb_edition_key, results, DEFAULT_CACHE_EXPIRATION)

    if not results:
        return {}
    return results
