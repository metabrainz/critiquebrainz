from typing import List
import uuid
from brainzutils import cache
import sqlalchemy
import critiquebrainz.frontend.external.bookbrainz_db as db
import critiquebrainz.frontend.external.bookbrainz_db.exceptions as bb_exceptions
from critiquebrainz.frontend.external.bookbrainz_db import DEFAULT_CACHE_EXPIRATION


def get_mapped_relationships(relation_types):
    """Get relation types mapped to their case sensitive name in bookbrainz.
    relationship_type table.
    
    Args:
        relation_types (list): List of relation types.
    Returns:
        List of mapped relation types.
    """
    mapped_relation_types = []
    relation_types = [relation_type.lower() for relation_type in relation_types]
    with db.bb_engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT
                label
            FROM bookbrainz.relationship_type
        """))
        relationships = [relationship[0] for relationship in result.fetchall()]
        relationships_mapping = {relationship.lower(): relationship for relationship in relationships}

        for relation_type in relation_types:
            if relation_type not in relationships_mapping:
                raise bb_exceptions.InvalidTypeError("Bad release_types: {rtype} is not supported".format(rtype=relation_type))
            else:
                mapped_relation_types.append(relationships_mapping[relation_type])

    return mapped_relation_types


def fetch_relationships(relationship_set_id: int, relation_types: List) -> List:
    """
    Fetch relationships from the database.
    """
    key = cache.gen_key('bb_relationship', relationship_set_id)
    relationships = cache.get(key)
    relation_types = get_mapped_relationships(relation_types)
    if not relationships:
        with db.bb_engine.connect() as connection:
            result = connection.execute(sqlalchemy.text("""
                SELECT
                    rel.id as id,
                    reltype.label as label,
                    rel.source_bbid as source_bbid,
                    rel.target_bbid as target_bbid,
                    reltype.target_entity_type as target_entity_type,
                    reltype.source_entity_type as source_entity_type
                FROM bookbrainz.relationship_set__relationship rels
                LEFT JOIN bookbrainz.relationship rel on rels.relationship_id = rel.id
                LEFT JOIN bookbrainz.relationship_type reltype on rel.type_id = reltype.id
                WHERE rels.set_id = :relationship_set_id
                AND reltype.label in :relation_types
            """), {'relationship_set_id': relationship_set_id, 'relation_types': tuple(relation_types)})
            relationships = result.fetchall()
            relationships = [dict(relationship) for relationship in relationships]
            for relationship in relationships:
                relationship['source_bbid'] = str(relationship['source_bbid'])
                relationship['target_bbid'] = str(relationship['target_bbid'])
            cache.set(key, relationships, DEFAULT_CACHE_EXPIRATION)

    if not relationships:
        return None
    return relationships
