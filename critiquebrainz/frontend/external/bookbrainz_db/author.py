import uuid
from brainzutils import cache
from typing import List
import sqlalchemy
import critiquebrainz.frontend.external.bookbrainz_db as db 
from critiquebrainz.frontend.external.bookbrainz_db import DEFAULT_CACHE_EXPIRATION
from critiquebrainz.frontend.external.bookbrainz_db.identifiers import fetch_bb_external_identifiers
from critiquebrainz.frontend.external.bookbrainz_db.relationships import fetch_relationships, AUTHOR_WORK_AUTHOR_REL_ID

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
                             FILTER (WHERE area IS NOT NULL),
                             '[]'
                             ) as area_info
			   FROM author
		  LEFT JOIN musicbrainz.area area 
				 ON begin_area_id = area.id
				 OR end_area_id = area.id
				 OR area_id = area.id
          LEFT JOIN musicbrainz.gender
                 ON gender_id = gender.id
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
				author['identifiers'] = fetch_bb_external_identifiers(author['identifier_set_id'])
				author['rels'] = fetch_relationships( author['relationship_set_id'], [AUTHOR_WORK_AUTHOR_REL_ID])
				results[author['bbid']] = author

			cache.set(bb_author_key, results, DEFAULT_CACHE_EXPIRATION)

	if not results:
		return {}
	return results
