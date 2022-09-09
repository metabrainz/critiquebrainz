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

def fetch_relationships(relationship_set_id: int, relation_types_id: List, ordering_type=None) -> List:
    """
    Fetch relationships from the database.
    Args:
        relationship_set_id (int): ID of the relationship set.
        relation_types (list): List of relation types.
        ordering_type (int): ID of the ordering type. (optional)

    Returns:
        List of relationships of the given types.

    """
    if not relationship_set_id:
        return []

    key = cache.gen_key('bb_relationship', relationship_set_id, relation_types_id, ordering_type)
    relationships = cache.get(key)
    if not relationships:

        query_params = {
            'relationship_set_id': relationship_set_id,
            'relation_types_id': tuple(relation_types_id),
        }

        order_by_clause = ''
        if ordering_type:
            order_by_clause = """
                ORDER BY CASE
                    WHEN :ordering_type = 2
                        THEN (attributes->>'position')::int
                    ELSE (attributes->>'number')::int
                END
            """
            query_params['ordering_type'] = ordering_type

        with db.bb_engine.connect() as connection:
            result = connection.execute(sqlalchemy.text("""
                WITH intermediate AS (
                     SELECT rel.id as id,
                            reltype.label as label,
                            rel.source_bbid::text as source_bbid,
                            rel.target_bbid::text as target_bbid,
                            reltype.target_entity_type as target_entity_type,
                            reltype.source_entity_type as source_entity_type,
                            COALESCE( 
                                jsonb_object_agg(relatttype.name, relatttext.text_value)
                                FILTER (WHERE relatts IS NOT NULL),
                                '[]'
                            ) as attributes
                       FROM relationship_set__relationship rels
                  LEFT JOIN relationship rel ON rels.relationship_id = rel.id
                  LEFT JOIN relationship_type reltype ON rel.type_id = reltype.id
                  LEFT JOIN relationship_attribute_set__relationship_attribute relatts ON rel.attribute_set_id = relatts.set_id
                  LEFT JOIN relationship_attribute relatt ON relatts.attribute_id = relatt.id
                  LEFT JOIN relationship_attribute_type relatttype ON relatt.attribute_type = relatttype.id
                  LEFT JOIN relationship_attribute_text_value relatttext ON relatts.attribute_id = relatttext.attribute_id
                      WHERE rels.set_id = :relationship_set_id
                        AND reltype.id in :relation_types_id
                   GROUP BY rel.id,
                            reltype.label,
                            rel.source_bbid,
                            rel.target_bbid,
                            reltype.target_entity_type,
                            reltype.source_entity_type
                ) SELECT *
                    FROM intermediate
                    {order_by_clause}
            """.format(order_by_clause=order_by_clause)
            ), query_params)
            relationships = result.fetchall()
            relationships = [dict(relationship) for relationship in relationships]
            cache.set(key, relationships, DEFAULT_CACHE_EXPIRATION)

    if not relationships:
        return []
    return relationships
