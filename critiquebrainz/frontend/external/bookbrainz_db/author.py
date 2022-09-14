import uuid
from brainzutils import cache
from typing import List
import sqlalchemy
import critiquebrainz.frontend.external.bookbrainz_db as db
from critiquebrainz.frontend.external.bookbrainz_db import DEFAULT_CACHE_EXPIRATION
from critiquebrainz.frontend.external.bookbrainz_db.identifiers import process_bb_identifiers


def get_author_by_bbid(bbid: str) -> dict:
	"""
	Get info related to an author using its BookBrainz ID.
	Args:
		bbid : BBID of the author.
	Returns:
		A dictionary containing the basic information related to the author.
		It includes the following keys:
			- bbid: BookBrainz ID of the author.
			- name: Name of the author.
			- sort_name: Sort name of the author.
			- author_type: Type of the author.
			- disambiguation: Disambiguation of the author.
			- identifiers: A list of dictionaries containing the basic information on the identifiers.
			- rels: A list of dictionaries containing the basic information on the relationships.
		
		Returns an empty dictionary if the author is not found.
	"""
	author = fetch_multiple_authors([bbid])
	if not author:
		return {}
	return author[bbid]


def fetch_multiple_authors(bbids: List[str]) -> dict:
	"""
	Get info related to multiple authors using their BookBrainz IDs. 
	Args:
		bbids (list): List of BBID of authors.
	Returns:
		A dictionary containing info of multiple authors keyed by their BBID.
	"""

	if bbids == []:
		return {}

	bbids = [str(uuid.UUID(bbid)) for bbid in bbids]

	bb_author_key = cache.gen_key('authors', bbids)
	results = cache.get(bb_author_key)
	if not results:
		with db.bb_engine.connect() as connection:
			result = connection.execute(sqlalchemy.text("""
				SELECT 
					bbid::text,
					author.name,
					sort_name,
					author_type,
					disambiguation,
					identifier_set_id,
					relationship_set_id,
					area_id,
					begin_year,
					begin_month,
					begin_day,
					begin_area_id,
					end_year,
					end_month,
					end_day,
					end_area_id,
					author.ended,
					gender.name as gender,
					COALESCE (json_agg(area)
							 FILTER (WHERE area.name IS NOT NULL),
							 '[]'
							 ) as area_info,
					COALESCE (json_agg(DISTINCT relationships)
							 FILTER (WHERE relationships IS NOT NULL),
							 '[]'
							 ) as rels,
					COALESCE (json_agg(DISTINCT identifiers)
							 FILTER (WHERE identifiers IS NOT NULL),
							 '[]'
							 ) as identifiers
			   FROM author
		  LEFT JOIN musicbrainz.area area
				 ON begin_area_id = area.id
				 OR end_area_id = area.id
				 OR area_id = area.id
		  LEFT JOIN musicbrainz.gender
				 ON gender_id = gender.id
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
						  WHERE rels.set_id = author.relationship_set_id
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
							WHERE idens.set_id = author.identifier_set_id
                     ) AS identifiers ON TRUE
			   WHERE bbid IN :bbids
				 AND master = 't'
			GROUP BY bbid,
					 author.name,
					 sort_name,
					 author_type,
					 disambiguation,
					 identifier_set_id,
					 relationship_set_id,
					 area_id,
					 begin_year,
					 begin_month,
					 begin_day,
					 begin_area_id,
					 end_year,
					 end_month,
					 end_day,
					 end_area_id,
					 author.ended,
					 gender.name
			"""), {'bbids': tuple(bbids)})

			authors = result.mappings()
			results = {}
			for author in authors:
				author = dict(author)
				author['bbid'] = str(author['bbid'])
				author['identifiers'] = process_bb_identifiers(author['identifiers'])
				results[author['bbid']] = author

			cache.set(bb_author_key, results, DEFAULT_CACHE_EXPIRATION)

	if not results:
		return {}
	return results
