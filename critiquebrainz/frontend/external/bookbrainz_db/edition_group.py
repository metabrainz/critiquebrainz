import uuid
from brainzutils import cache
from typing import List
import sqlalchemy
import critiquebrainz.frontend.external.bookbrainz_db as db 
from critiquebrainz.frontend.external.bookbrainz_db import DEFAULT_CACHE_EXPIRATION
from critiquebrainz.frontend.external.bookbrainz_db.identifiers import process_bb_identifiers
from critiquebrainz.frontend.external.bookbrainz_db.relationships import EDITION_WORK_CONTAINS_REL_ID


def get_edition_group_by_bbid(bbid: str) -> dict:
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

        Returns an empty dictionary if the edition group is not found.

    """
    edition_group = fetch_multiple_edition_groups([bbid])
    if not edition_group:
        return {}
    return edition_group[bbid]


def fetch_multiple_edition_groups(bbids: List[str]) -> dict:
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
                            ) as author_credits,
                    COALESCE (json_agg(DISTINCT relationships)
							 FILTER (WHERE relationships IS NOT NULL),
							 '[]'
							 ) as rels,
					COALESCE (json_agg(DISTINCT identifiers)
							 FILTER (WHERE identifiers IS NOT NULL),
							 '[]'
							 ) as identifiers
               FROM edition_group 
          LEFT JOIN author_credit_name acn ON acn.author_credit_id = edition_group.author_credit_id 
          LEFT JOIN LATERAL (
                     SELECT rel.id as id,
							reltype.id as relationship_type_id,
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
					  WHERE rels.set_id = edition_group.relationship_set_id
				   GROUP BY rel.id,
							reltype.id,
							reltype.label,
							rel.source_bbid,
							rel.target_bbid,
							reltype.target_entity_type,
							reltype.source_entity_type
                ) AS relationships ON TRUE
          LEFT JOIN LATERAL (
                     SELECT iden.type_id as type_id,
                            idtype.label as label,
                            idtype.display_template as url_template,
                            iden.value as value
                       FROM identifier_set__identifier idens
				  LEFT JOIN identifier iden on idens.identifier_id = iden.id
				  LEFT JOIN identifier_type idtype on iden.type_id = idtype.id
					  WHERE idens.set_id = edition_group.identifier_set_id
                ) AS identifiers ON TRUE
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
            
            edition_groups = result.mappings()
            results = {}
            for edition_group in edition_groups:
                edition_group = dict(edition_group)
                edition_group['identifiers'] = process_bb_identifiers(edition_group['identifiers'])
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
                """), {'bbid': str(bbid), 'relationship_type_id': EDITION_WORK_CONTAINS_REL_ID})

            works = result.mappings()
            work_bbids = []

            for work in works:
                work = dict(work)
                work_bbids.append(work['target_bbid'])

            results = work_bbids
            cache.set(bb_edition_group_work, results, DEFAULT_CACHE_EXPIRATION)

    if not results:
        return []
    return results
