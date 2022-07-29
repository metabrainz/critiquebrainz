import uuid
from brainzutils import cache
from typing import List
import sqlalchemy
import critiquebrainz.frontend.external.bookbrainz_db as db 
from critiquebrainz.frontend.external.bookbrainz_db import DEFAULT_CACHE_EXPIRATION
from critiquebrainz.frontend.external.bookbrainz_db.identifiers import fetch_bb_external_identifiers
from critiquebrainz.frontend.external.bookbrainz_db.relationships import fetch_relationships

def get_publisher_by_bbid(bbid: uuid.UUID) -> dict:
	"""
	Get info related to a publisher using its BookBrainz ID.
    Args:
		bbid: BookBrainz ID of the publisher.
	Returns:
		A dictionary containing the following keys:
			- bbid: BookBrainz ID of the publisher.
			- name: Name of the publisher.
			- sort_name: Sort name of the publisher.
			- publisher_type: Type of the publisher.
			- disambiguation: Disambiguation of the publisher.
			- identifiers: A list of dictionaries containing the basic information on the identifiers.
            - rels: A list of dictionaries containing the basic information on the relationships.
	"""

	publisher = fetch_multiple_publishers([bbid])
	if not publisher:
		return None
	return publisher[bbid]


def fetch_multiple_publishers(bbids: List[uuid.UUID]) -> dict:
	"""
	Get info related to multiple publishers using their BookBrainz IDs. 
	Args:
		bbids (list): List of BBID of publishers.
	Returns:
		A dictionary containing info of multiple publishers keyed by their BBID.
	"""
	if bbids == []:
		return {}
	
	bbids = [str(uuid.UUID(bbid)) for bbid in bbids]

	bb_publisher_key = cache.gen_key('publishers', bbids)
	results = cache.get(bb_publisher_key)
	if not results:
		with db.bb_engine.connect() as connection:
			result = connection.execute(sqlalchemy.text("""
				SELECT 
					bbid::text,
					publisher.name,
					sort_name,
					publisher_type,
					disambiguation,
					identifier_set_id,
					relationship_set_id,
					area.gid::text as area_mbid,
                    area.name as area_name,
					begin_year,
					begin_month,
					begin_day,
					end_year,
					end_month,
					end_day,
					publisher.ended
			   FROM publisher
		  LEFT JOIN musicbrainz.area 
				 ON publisher.area_id = area.id
			  WHERE bbid IN :bbids
				AND master = 't'
			"""), {'bbids': tuple(bbids)})

			publishers = result.fetchall()
			results = {}
			for publisher in publishers:
				publisher = dict(publisher)
				publisher['bbid'] = str(publisher['bbid'])
				publisher['identifiers'] = fetch_bb_external_identifiers(publisher['identifier_set_id'])
				publisher['rels'] = fetch_relationships( publisher['relationship_set_id'], ['Publisher'])
				results[publisher['bbid']] = publisher

			cache.set(bb_publisher_key, results, DEFAULT_CACHE_EXPIRATION)

	if not results:
		return {}
	return results
