ALTER TABLE review ADD COLUMN blurb BOOLEAN;
ALTER TABLE review DROP CONSTRAINT review_entity_id_user_id_key;
CREATE UNIQUE INDEX review_entity_user_id_index ON review (entity_id, user_id) WHERE (blurb='f' OR blurb is NULL)

-- check if the review is marked a blurb, then check it's character length
CREATE OR REPLACE FUNCTION check_blurb_length() RETURNS trigger AS
$CHECK_LENGTH_BODY$
BEGIN
    IF (SELECT blurb FROM review JOIN revision ON review.id=revision.review_id WHERE review.id = NEW.review_id ORDER BY timestamp DESC LIMIT 1) = 't' THEN
        IF char_length(NEW.text) > 280 OR char_length(NEW.text) IS NULL THEN
            IF (SELECT count(*) FROM revision WHERE review_id=NEW.review_id) = 0 THEN
                DELETE FROM review WHERE id=NEW.review_id;
            END IF;
            RAISE EXCEPTION 'Length of Blurb is not within the range (1 - 280)';
        END IF;
    END IF;
    RETURN NULL;
END;
$CHECK_LENGTH_BODY$ LANGUAGE plpgsql;

CREATE TRIGGER check_blurb_length AFTER INSERT ON revision FOR EACH ROW EXECUTE PROCEDURE check_blurb_length();

