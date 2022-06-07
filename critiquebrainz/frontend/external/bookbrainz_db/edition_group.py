import uuid
from brainzutils import cache
from typing import List
import sqlalchemy
import critiquebrainz.frontend.external.bookbrainz_db as db 
from critiquebrainz.frontend.external.bookbrainz_db import DEFAULT_CACHE_EXPIRATION
from critiquebrainz.frontend.external.bookbrainz_db.identifiers import fetch_identifiers
from critiquebrainz.frontend.external.bookbrainz_db.relationships import fetch_relationships


def get_edition_group_by_bbid(bbid: uuid.UUID) -> dict:
    """
    Get info related to an edition group using its BookBrainz ID.
    Args:
        bbid : BBID of the edition group.
    Returns:
        A dictionary containing the basic information related to the edition group.
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

    key = cache.gen_key('edition-groups', bbids)
    edition_groups = cache.get(key)
    if not edition_groups:
        with db.bb_engine.connect() as connection:
            result = connection.execute(sqlalchemy.text("""
                SELECT 
                    e.bbid as bbid,
                    al.name as name,
                    al.sort_name as sort_name,
                    al.primary as primary,
                    egd.identifier_set_id as identifier_set_id,
                    egd.relationship_set_id as relationship_set_id,
                    egd.author_credit_id as author_credit_id,
                    disam.comment as disambiguation_comment,
                    egtype.label as label,
                    acn.author_bbid as author_bbid,
                    acn.name as author_name
                
                FROM bookbrainz.entity e
                LEFT JOIN bookbrainz.edition_group_header c ON c.bbid = e.bbid
                LEFT JOIN bookbrainz.edition_group_revision cr on c.master_revision_id = cr.id
                LEFT JOIN bookbrainz.edition_group_data egd ON cr.data_id = egd.id
                LEFT JOIN bookbrainz.alias_set als ON egd.alias_set_id = als.id
                LEFT JOIN bookbrainz.alias al ON als.default_alias_id = al.id
                LEFT JOIN bookbrainz.edition_group_type egtype ON egd.type_id = egtype.id
                LEFT JOIN bookbrainz.disambiguation disam on egd.disambiguation_id = disam.id
                LEFT JOIN bookbrainz.author_credit_name acn on egd.author_credit_id = acn.author_credit_id
                WHERE e.bbid in :bbids;
                
                """), {'bbids': tuple(bbids)})
            
            edition_groups = result.fetchall()
            results = {}
            for edition_group in edition_groups:
                edition_group = dict(edition_group)
                edition_group['bbid'] = str(edition_group['bbid'])
                edition_group['identifiers'] = fetch_identifiers(edition_group['identifier_set_id'])
                edition_group['rels'] = fetch_relationships( edition_group['relationship_set_id'], ['Edition'])
                results[edition_group['bbid']] = edition_group
            
            edition_groups = results
            cache.set(key, edition_groups, DEFAULT_CACHE_EXPIRATION)
    
    if not edition_groups:
        return None
    return edition_groups
