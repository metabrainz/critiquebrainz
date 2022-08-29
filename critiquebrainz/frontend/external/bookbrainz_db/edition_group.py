import uuid
from brainzutils import cache
from typing import List
import sqlalchemy
import critiquebrainz.frontend.external.bookbrainz_db as db 
from critiquebrainz.frontend.external.bookbrainz_db import DEFAULT_CACHE_EXPIRATION, BB_RELATIONSHIP_EDITION_WORK_CONTAINS
from critiquebrainz.frontend.external.bookbrainz_db.identifiers import fetch_bb_external_identifiers
from critiquebrainz.frontend.external.bookbrainz_db.relationships import fetch_relationships


def get_edition_group_by_bbid(bbid: uuid.UUID) -> dict:
    """
    Get info related to an edition group using its BookBrainz ID.
    Args:
        bbid : BBID of the edition group.
    Returns:
        A dictionary containing the basic information related to the edition group.
        It includes the following keys:
            - bbid: BookBrainz ID of the edition group.
            - name: Name of the edition group.
            - sort_name: Sort name of the edition group.
            - edition_group_type: Type of the edition group.
            - disambiguation: Disambiguation of the edition group.
            - identifiers: A list of dictionaries containing the basic information on the identifiers.
            - rels: A list of dictionaries containing the basic information on the relationships.
            - author_credits: A list of dictionaries containing the basic information on the author credits.

        Returns None if the edition group is not found.

    """
    edition_group = fetch_multiple_edition_groups([bbid])
    if not edition_group:
        return None
    return edition_group[bbid]


def fetch_multiple_edition_groups(bbids: List[uuid.UUID]) -> dict:
    """
    Get info related to multiple edition groups using their BookBrainz IDs. 
    Args:
        bbids (list): List of BBID of edition groups.
    Returns:
        A dictionary containing info of multiple edition groups keyed by their BBID.
    """
    if bbids == []:
        return {}

    bbids = [str(uuid.UUID(bbid)) for bbid in bbids]

    bb_edition_group_key = cache.gen_key('edition-groups', bbids)
    results = cache.get(bb_edition_group_key)
    if not results:
        with db.bb_engine.connect() as connection:
            result = connection.execute(sqlalchemy.text("""
                SELECT 
                    bbid::text,
                    edition_group.name,
                    sort_name,
                    edition_group_type,
                    disambiguation,
                    identifier_set_id,
                    relationship_set_id,
                    COALESCE( json_agg( acn ORDER BY "position" ASC )
                              FILTER (WHERE acn IS NOT NULL),
                              '[]'
                            ) as author_credits
               FROM edition_group 
          LEFT JOIN author_credit_name acn ON acn.author_credit_id = edition_group.author_credit_id 
              WHERE bbid in :bbids
                AND master = 't'
                AND data_id IS NOT NULL
           GROUP BY bbid,
                    edition_group.name,
                    sort_name,
                    edition_group_type,
                    disambiguation,
                    identifier_set_id,
                    relationship_set_id
                """), {'bbids': tuple(bbids)})
            
            edition_groups = result.fetchall()
            results = {}
            for edition_group in edition_groups:
                edition_group = dict(edition_group)
                edition_group['identifiers'] = fetch_bb_external_identifiers(edition_group['identifier_set_id'])
                edition_group['rels'] = fetch_relationships( edition_group['relationship_set_id'], ['Edition'])
                results[edition_group['bbid']] = edition_group
            
            edition_groups = results
            cache.set(bb_edition_group_key, results, DEFAULT_CACHE_EXPIRATION)
    
    if not results:
        return {}
    return results


def fetch_works_for_edition_group(bbid: uuid.UUID):
    """
    Get works linked to an edition group using its BookBrainz ID.

    Args:
        bbid : BBID of the edition group.
    Returns:
        A tuple containing the list of work bbids linked to edition group.

    """

    bb_edition_group_work = cache.gen_key('bb-edition-groups-works', bbid)
    results = cache.get(bb_edition_group_work)
    if not results:
        with db.bb_engine.connect() as connection:
            result = connection.execute(sqlalchemy.text("""
             SELECT DISTINCT(rel.target_bbid::text)
               FROM edition_group
         INNER JOIN edition ON edition.edition_group_bbid = edition_group.bbid
         INNER JOIN relationship_set__relationship rels on rels.set_id = edition.relationship_set_id
          LEFT JOIN relationship rel on rels.relationship_id = rel.id
              WHERE edition_group.bbid = :bbid
                AND edition_group.master = 't'
                AND edition_group.data_id IS NOT NULL
                AND edition.master = 't'
                AND edition.data_id IS NOT NULL
                AND rel.type_id = :relationship_type_id
                """), {'bbid': str(bbid), 'relationship_type_id': BB_RELATIONSHIP_EDITION_WORK_CONTAINS})

            works = result.fetchall()
            work_bbids = []

            for work in works:
                work = dict(work)
                work_bbids.append(work['target_bbid'])

            results = work_bbids
            cache.set(bb_edition_group_work, results, DEFAULT_CACHE_EXPIRATION)

    if not results:
        return []
    return results
