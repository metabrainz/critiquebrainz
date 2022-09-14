import uuid
from brainzutils import cache
from typing import List
import sqlalchemy
import critiquebrainz.frontend.external.bookbrainz_db as db
from critiquebrainz.frontend.external.bookbrainz_db import DEFAULT_CACHE_EXPIRATION
from critiquebrainz.frontend.external.bookbrainz_db.identifiers import process_bb_identifiers
from critiquebrainz.frontend.external.bookbrainz_db.relationships import SERIES_REL_MAP
from critiquebrainz.frontend.external.bookbrainz_db.author import fetch_multiple_authors
from critiquebrainz.frontend.external.bookbrainz_db.edition import fetch_multiple_editions
from critiquebrainz.frontend.external.bookbrainz_db.edition_group import fetch_multiple_edition_groups
from critiquebrainz.frontend.external.bookbrainz_db.literary_work import fetch_multiple_literary_works
from critiquebrainz.frontend.external.bookbrainz_db.publisher import fetch_multiple_publishers



def get_series_by_bbid(bbid: str) -> dict:
    """
    Get info related to a series using its BookBrainz ID.
    Args:
        bbid: BookBrainz ID of the series.
    Returns:
        A dictionary containing the basic information related to the series.
        It includes the following keys:
            - bbid: BookBrainz ID of the series.
            - name: Name of the series.
            - sort_name: Sort name of the series.
            - series_type: Type of the series.
            - disambiguation: Disambiguation of the series.
            - identifiers: A list of dictionaries containing the basic information on the identifiers.
            - rels: A list of dictionaries containing the basic information on the relationships.

        Returns empty dictionary if the series is not found.
    """

    series = fetch_multiple_series([bbid])
    if not series:
        return {}
    return series[bbid]


def fetch_multiple_series(bbids: List[str]) -> dict:
    """
    Get info related to multiple series using their BookBrainz IDs. 
    Args:
        bbids (list): List of BBID of series.
    Returns:
        A dictionary containing info of multiple series keyed by their BBID.
    """
    if bbids == []:
        return {}

    bbids = [str(uuid.UUID(bbid)) for bbid in bbids]

    bb_series_key = cache.gen_key('series', bbids)
    results = cache.get(bb_series_key)
    if not results:
        with db.bb_engine.connect() as connection:
            result = connection.execute(sqlalchemy.text("""
                SELECT 
                    bbid::text,
                    series.name,
                    sort_name,
                    entity_type as series_type,
                    disambiguation,
                    identifier_set_id,
                    relationship_set_id,
                    series_ordering_type.label as series_ordering_type,
                    series_ordering_type.id as series_ordering_type_id,
                    COALESCE (json_agg(DISTINCT relationships)
                             FILTER (WHERE relationships IS NOT NULL),
                             '[]'
                             ) as rels,
                    COALESCE (json_agg(DISTINCT identifiers)
                             FILTER (WHERE identifiers IS NOT NULL),
                             '[]'
                             ) as identifiers
               FROM series
          LEFT JOIN series_ordering_type
                 ON series.ordering_type_id = series_ordering_type.id
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
					  WHERE rels.set_id = series.relationship_set_id
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
					  WHERE idens.set_id = series.identifier_set_id
                ) AS identifiers ON TRUE
              WHERE bbid IN :bbids
                AND master = 't'
                AND entity_type IS NOT NULL
           GROUP BY bbid,
                    series.name,
                    sort_name,
                    entity_type,
                    disambiguation,
                    identifier_set_id,
                    relationship_set_id,
                    series_ordering_type.label,
                    series_ordering_type.id
            """), {'bbids': tuple(bbids)})

            data = result.mappings()
            results = {}
            for series in data:
                series = dict(series)
                series['bbid'] = str(series['bbid'])
                series['identifiers'] = process_bb_identifiers(series['identifiers'])

                series_rels = []
                for rel in series['rels']:
                    if rel['relationship_type_id'] == SERIES_REL_MAP[series['series_type']]:
                        series_rels.append(rel)

                if series['series_ordering_type_id'] == 2:
                    series['rels'] = sorted(series_rels, key=lambda i: (
                        i['attributes']['position'] is None, i['attributes']['position']))
                else:
                    series['rels'] = sorted(series_rels, key=lambda i: (
                        i['attributes']['number'] is None, i['attributes']['number']))

                results[series['bbid']] = series

            cache.set(bb_series_key, results, DEFAULT_CACHE_EXPIRATION)

    if not results:
        return {}
    return results


def fetch_series_rels_info(entity_type: str, bbids: List[str]) -> dict:
    """
    Get info related to multiple series using their BookBrainz IDs.
    Args:
        - entity_type: Type of the entity.
        - bbids (list): List of the rels of Series.

    Returns:
        A dictionary containing information of the rels of series keyed by their BBID.
    """

    if bbids == []:
        return {}

    bb_series_rels_info_key = cache.gen_key('series_rels_info', bbids)
    results = cache.get(bb_series_rels_info_key)
    if not results:
        if entity_type == 'Author':
            results = fetch_multiple_authors(bbids)

        elif entity_type == 'Edition':
            results = fetch_multiple_editions(bbids)

        elif entity_type == 'EditionGroup':
            results = fetch_multiple_edition_groups(bbids)

        elif entity_type == 'Publisher':
            results = fetch_multiple_publishers(bbids)

        elif entity_type == 'Work':
            results = fetch_multiple_literary_works(bbids)

        cache.set(bb_series_rels_info_key, results, DEFAULT_CACHE_EXPIRATION)

    if not results:
        return {}
    return results
