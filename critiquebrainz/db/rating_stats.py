import sqlalchemy

from critiquebrainz import db

def get_stats(entity_id, entity_type):
    """Gets the average rating and the rating statistics of the entity

    It is done by selecting ratings from the latest revisions of all reviews
    for a given entity.

    Args:
        entity_id (uuid): ID of the entity
        entity_type (str): Type of the entity
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            WITH LatestRevisions AS (
                SELECT review_id,
                       MAX("timestamp") created_at
                  FROM revision
                 WHERE review_id in (
                           SELECT id
                             FROM review
                            WHERE entity_id = :entity_id
                              AND entity_type = :entity_type
                              AND is_hidden = 'f')
              GROUP BY review_id
            )
            SELECT rating
              FROM revision
        INNER JOIN LatestRevisions
                ON revision.review_id = LatestRevisions.review_id
               AND revision.timestamp = LatestRevisions.created_at
        """), {
            "entity_id": entity_id,
            "entity_type": entity_type,
        })
        row = result.fetchall()

    ratings_stats = {1: 0, 2: 0, 3: 0, 4:0, 5:0}
    if row == []:
        return ratings_stats, 0

    ratings =  [r[0]/20 for r in row if r[0] is not None]

    for rating in ratings:
        ratings_stats[rating] += 1
    
    if ratings:
        average_rating = sum(ratings)/len(ratings)
    else:
        average_rating = 0

    return ratings_stats, average_rating