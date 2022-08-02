import uuid
from brainzutils import cache
from typing import List
import sqlalchemy
import critiquebrainz.frontend.external.bookbrainz_db as db
from critiquebrainz.frontend.external.bookbrainz_db import DEFAULT_CACHE_EXPIRATION
from critiquebrainz.frontend.external.bookbrainz_db.identifiers import fetch_bb_external_identifiers
from critiquebrainz.frontend.external.bookbrainz_db.relationships import fetch_relationships

WORK_TYPE_FILTER_OPTIONS = ('Novel', 'Short Story', 'Poem')

def get_literary_work_by_bbid(bbid: uuid.UUID) -> dict:
    """
    Get info related to a literary work using its BookBrainz ID.
    Args:
        bbid : BBID of the literary work.
    Returns:
        A dictionary containing the basic information related to the literary work.
        It includes the following keys:
            - bbid: BookBrainz ID of the literary work.
            - name: Name of the literary work.
            - sort_name: Sort name of the literary work.
            - work_type: Type of the work.
            - disambiguation: Disambiguation of the literary work.
            - identifiers: A list of dictionaries containing the basic information on the identifiers.
            - rels: A list of dictionaries containing the basic information on the relationships.

        Returns None if the literary work is not found.
    """
    literary_work = fetch_multiple_literary_works([bbid])
    if not literary_work:
        return None
    return literary_work[bbid]


def fetch_multiple_literary_works(bbids: List[uuid.UUID], work_type=None, limit=None, offset=0) -> dict:
    """
    Get info related to multiple literary works using their BookBrainz IDs. 
    Args:
        bbids (list): List of BBID of literary works.
        work_type (str): Filter the results by work type.
        limit (int): Limit the number of results.
        offset (int): Offset the results.
    Returns:
        A dictionary containing info of multiple literary works keyed by their BBID.
    """
    if bbids == []:
        return {}

    bbids = [str(uuid.UUID(bbid)) for bbid in bbids]

    if limit is None:
        limit = len(bbids)

    if work_type is None:
        work_type_filter_string = ''
    elif work_type in WORK_TYPE_FILTER_OPTIONS:
        work_type_filter_string = 'AND work_type = \'%s\'' % work_type
    elif work_type == 'other':
        work_type_filter_string = 'AND ( work_type IS NULL OR work_type NOT IN (\'%s\'))' % '\', \''.join(
            WORK_TYPE_FILTER_OPTIONS)

    bb_literary_work_key = cache.gen_key('literary-works', bbids, limit, offset, work_type)
    results = cache.get(bb_literary_work_key)
    if not results:
        with db.bb_engine.connect() as connection:
            result = connection.execute(sqlalchemy.text("""
                SELECT
                    bbid::text,
                    work.name,
                    sort_name,
                    work_type,
                    disambiguation,
                    identifier_set_id,
                    relationship_set_id,
                    COALESCE (json_agg(mbl.name)
                             FILTER (WHERE mbl IS NOT NULL),
                             '[]'
                             ) as languages
                FROM work
           LEFT JOIN bookbrainz.language_set__language lsl ON lsl.set_id = work.language_set_id
           LEFT JOIN musicbrainz.language mbl on mbl.id = lsl.language_id
                WHERE bbid IN :bbids
                    AND master = 't'
                    {work_type_filter_string}
               GROUP BY bbid,
                        work.name,
                        sort_name,
                        work_type,
                        disambiguation,
                        identifier_set_id,
                        relationship_set_id
                LIMIT :limit
               OFFSET :offset
            """.format(work_type_filter_string=work_type_filter_string)
            ), {'bbids': tuple(bbids), 'limit': limit, 'offset': offset})

            literary_works = result.fetchall()
            results = {}
            for literary_work in literary_works:
                literary_work = dict(literary_work)
                literary_work['identifiers'] = fetch_bb_external_identifiers(literary_work['identifier_set_id'])
                literary_work['rels'] = fetch_relationships(literary_work['relationship_set_id'], ['Edition'])
                results[literary_work['bbid']] = literary_work

            cache.set(bb_literary_work_key, results, DEFAULT_CACHE_EXPIRATION)

    if not results:
        return {}
    return results
