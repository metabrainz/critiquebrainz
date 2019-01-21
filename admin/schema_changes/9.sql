BEGIN;

ALTER TABLE review ADD COLUMN published_on TIMESTAMP;

UPDATE review
   SET published_on = sub.latest
  FROM ( SELECT review_id, MAX(rv.timestamp) as latest
           FROM review r
           JOIN revision rv
             ON r.id = rv.review_id
       GROUP BY review_id
       ) AS sub
 WHERE is_draft = 'f' AND sub.review_id = id;

COMMIT;
