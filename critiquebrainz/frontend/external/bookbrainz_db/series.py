import uuid
from brainzutils import cache
from typing import List
import sqlalchemy
import critiquebrainz.frontend.external.bookbrainz_db as db
from critiquebrainz.frontend.external.bookbrainz_db import DEFAULT_CACHE_EXPIRATION
from critiquebrainz.frontend.external.bookbrainz_db.identifiers import fetch_bb_external_identifiers
from critiquebrainz.frontend.external.bookbrainz_db.relationships import fetch_relationships, SERIES_REL_MAP
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
                    series_ordering_type.label as series_ordering_type
               FROM series
          LEFT JOIN series_ordering_type
                 ON series.ordering_type_id = series_ordering_type.id
              WHERE bbid IN :bbids
                AND master = 't'
                AND entity_type IS NOT NULL
            """), {'bbids': tuple(bbids)})

            data = result.mappings()
            results = {}
            for series in data:
                series = dict(series)
                series['bbid'] = str(series['bbid'])
                series['identifiers'] = fetch_bb_external_identifiers(series['identifier_set_id'])
                series['rels'] = fetch_relationships(series['relationship_set_id'], [SERIES_REL_MAP[series['series_type']]])
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
