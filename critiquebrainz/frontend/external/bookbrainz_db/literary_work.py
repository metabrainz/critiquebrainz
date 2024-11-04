import uuid
from brainzutils import cache
from typing import List
import sqlalchemy
import critiquebrainz.frontend.external.bookbrainz_db as db
from critiquebrainz.frontend.external.bookbrainz_db import DEFAULT_CACHE_EXPIRATION
from critiquebrainz.frontend.external.bookbrainz_db.identifiers import process_bb_identifiers
from critiquebrainz.frontend.external.bookbrainz_db.relationships import EDITION_WORK_CONTAINS_REL_ID

WORK_TYPE_FILTER_OPTIONS = ('Novel', 'Short Story', 'Poem')


def get_literary_work_by_bbid(bbid: str) -> dict:
    """
    Get info related to a literary work using its BookBrainz ID.
    Args:
        bbid : BBID of the literary work.
    Returns:
        A dictionary containing the basic information related to the literary work.
        It includes the following keys:
            - bbid: BookBrainz ID of the literary work.
            - name: Name of the literary work.
            - sort_name: Sort name of the literary work.
            - work_type: Type of the work.
            - disambiguation: Disambiguation of the literary work.
            - identifiers: A list of dictionaries containing the basic information on the identifiers.
            - rels: A list of dictionaries containing the basic information on the relationships.

        Returns an  empty dictionary if the literary work is not found.
    """
    literary_work = fetch_multiple_literary_works([bbid])
    if not literary_work:
        return {}
    return literary_work[bbid]


def fetch_multiple_literary_works(bbids: List[str], work_type=None, limit=None, offset=0) -> dict:
    """
    Get info related to multiple literary works using their BookBrainz IDs. 
    Args:
        bbids (list): List of BBID of literary works.
        work_type (str): Filter the results by work type. It includes the following values:
            - Novel
            - Short Story
            - Poem
            - Other - all other work types like articles, plays, etc.
        limit (int): Limit the number of results.
        offset (int): Offset the results.
    Returns:
        A dictionary containing info of multiple literary works keyed by their BBID.
    """
    if bbids == []:
        return {}

    bbids = [str(uuid.UUID(bbid)) for bbid in bbids]

    query_params = {
        'bbids': tuple(bbids),
        'limit': limit,
        'offset': offset,
    }
    work_type_filter_string = ''
    if work_type in WORK_TYPE_FILTER_OPTIONS:
        work_type_filter_string = 'AND work_type = :work_type'
        query_params['work_type'] = work_type
    elif work_type == 'other':
        work_type_filter_string = 'AND ( work_type IS NULL OR work_type NOT IN :ommitted_work_types )'
        query_params['ommitted_work_types'] = WORK_TYPE_FILTER_OPTIONS

    bb_literary_work_key = cache.gen_key('literary-works', bbids, limit, offset, work_type)
    results = cache.get(bb_literary_work_key)
    if not results:
        with db.bb_engine.connect() as connection:
            result = connection.execute(sqlalchemy.text("""
                SELECT
                    bbid::text,
                    work.name,
                    sort_name,
                    work_type,
                    disambiguation,
                    identifier_set_id,
                    relationship_set_id,
                    COALESCE (json_agg(DISTINCT mbl.name)
                             FILTER (WHERE mbl IS NOT NULL),
                             '[]'
                             ) as languages,
                    COALESCE (json_agg(DISTINCT relationships)
                             FILTER (WHERE relationships IS NOT NULL),
                             '[]'
                             ) as rels,
                    COALESCE (json_agg(DISTINCT identifiers)
                             FILTER (WHERE identifiers IS NOT NULL),
                             '[]'
                             ) as identifiers
                FROM work
           LEFT JOIN bookbrainz.language_set__language lsl ON lsl.set_id = work.language_set_id
           LEFT JOIN musicbrainz.language mbl on mbl.id = lsl.language_id
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
                          WHERE rels.set_id = work.relationship_set_id
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
                            WHERE idens.set_id = work.identifier_set_id
                    ) AS identifiers ON TRUE
                WHERE bbid IN :bbids
                    AND master = 't'
                    AND data_id IS NOT NULL
                    {work_type_filter_string}
               GROUP BY bbid,
                        work.name,
                        sort_name,
                        work_type,
                        disambiguation,
                        identifier_set_id,
                        relationship_set_id
                LIMIT :limit
               OFFSET :offset
            """.format(work_type_filter_string=work_type_filter_string)
            ), query_params)

            literary_works = result.mappings()
            results = {}
            for literary_work in literary_works:
                literary_work = dict(literary_work)
                literary_work['identifiers'] = process_bb_identifiers(literary_work['identifiers'])
                results[literary_work['bbid']] = literary_work

            cache.set(bb_literary_work_key, results, DEFAULT_CACHE_EXPIRATION)

    if not results:
        return {}
    return results


def fetch_edition_groups_for_works(bbid: str) -> list:
    """
    Get edition groups for a literary work.
    Args:
        bbid : BBID of the literary work.
    Returns:
        A list containing the list of edition groups bbids linked to literary work.
    """
    bb_work_edition_groups_key = cache.gen_key('bb_work_edition_groups', bbid)
    results = cache.get(bb_work_edition_groups_key)
    if not results:
        with db.bb_engine.connect() as connection:
            result = connection.execute(sqlalchemy.text("""
             SELECT DISTINCT(edition.edition_group_bbid::text)
               FROM work
         INNER JOIN relationship_set__relationship rels on rels.set_id = work.relationship_set_id
          LEFT JOIN relationship rel on rels.relationship_id = rel.id
         INNER JOIN edition ON rel.source_bbid = edition.bbid
              WHERE work.bbid = :bbid
                AND work.master = 't'
                AND work.data_id IS NOT NULL
                AND edition.master = 't'
                AND edition.data_id IS NOT NULL
                AND rel.type_id = :relationship_type_id
                """), {'bbid': str(bbid), 'relationship_type_id': EDITION_WORK_CONTAINS_REL_ID})

            edition_groups = result.mappings()
            edition_group_bbids = []

            for edition_group in edition_groups:
                edition_group = dict(edition_group)
                edition_group_bbids.append(edition_group['edition_group_bbid'])

            results = edition_group_bbids
            cache.set(bb_work_edition_groups_key, results, DEFAULT_CACHE_EXPIRATION)

    if not results:
        return []
    return results
