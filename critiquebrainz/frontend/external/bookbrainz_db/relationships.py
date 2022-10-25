from typing import List
from brainzutils import cache
import sqlalchemy
import critiquebrainz.frontend.external.bookbrainz_db as db
from critiquebrainz.frontend.external.bookbrainz_db import DEFAULT_CACHE_EXPIRATION

AUTHOR_WORK_AUTHOR_REL_ID = 8
EDITION_EDITION_GROUP_EDITION_REL_ID = 3
EDITION_WORK_CONTAINS_REL_ID = 10
WORK_WORK_TRANSLATION_REL_ID = 56

SERIES_REL_MAP = {
    'Author': 70,
    'Edition': 72,
    'EditionGroup': 73,
    'Publisher': 74,
    'Work': 71,
}

def fetch_relationships(relationship_set_id: int, relation_types_id: List) -> List:
    """
    Fetch relationships from the database.
    """
    if not relationship_set_id:
        return []

    key = cache.gen_key('bb_relationship', relationship_set_id, relation_types_id)
    relationships = cache.get(key)
    if not relationships:
        with db.bb_engine.connect() as connection:
            result = connection.execute(sqlalchemy.text("""
                SELECT rel.id as id,
                       reltype.id as relation_type_id,
                       reltype.label as label,
                       rel.source_bbid::text as source_bbid,
                       rel.target_bbid::text as target_bbid,
                       reltype.target_entity_type as target_entity_type,
                       reltype.source_entity_type as source_entity_type
                  FROM relationship_set__relationship rels
             LEFT JOIN relationship rel on rels.relationship_id = rel.id
             LEFT JOIN relationship_type reltype on rel.type_id = reltype.id
                 WHERE rels.set_id = :relationship_set_id
                   AND reltype.id in :relation_types_id
            """), {'relationship_set_id': relationship_set_id, 'relation_types_id': tuple(relation_types_id)})
            relationships = result.fetchall()
            relationships = [dict(relationship) for relationship in relationships]
            cache.set(key, relationships, DEFAULT_CACHE_EXPIRATION)

    if not relationships:
        return []
    return relationships
