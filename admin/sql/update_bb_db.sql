-- Views --
BEGIN;

DROP VIEW bookbrainz.author;
DROP VIEW bookbrainz.edition;
DROP VIEW bookbrainz.edition_group;
DROP VIEW bookbrainz.publisher;
DROP VIEW bookbrainz.work;
DROP VIEW bookbrainz.series;

CREATE OR REPLACE VIEW bookbrainz.author AS
	SELECT
		e.bbid, ad.id AS data_id, ar.id AS revision_id, (ar.id = ah.master_revision_id) AS master, ad.annotation_id, ad.disambiguation_id, dis.comment disambiguation,
		als.default_alias_id, al."name", al.sort_name, ad.begin_year, ad.begin_month, ad.begin_day, ad.begin_area_id,
		ad.end_year, ad.end_month, ad.end_day, ad.end_area_id, ad.ended, ad.area_id,
		ad.gender_id, ad.type_id, atype.label as author_type, ad.alias_set_id, ad.identifier_set_id, ad.relationship_set_id, e.type
	FROM bookbrainz.author_revision ar
	LEFT JOIN bookbrainz.entity e ON e.bbid = ar.bbid
	LEFT JOIN bookbrainz.author_header ah ON ah.bbid = e.bbid
	LEFT JOIN bookbrainz.author_data ad ON ar.data_id = ad.id
	LEFT JOIN bookbrainz.alias_set als ON ad.alias_set_id = als.id
	LEFT JOIN bookbrainz.alias al ON al.id = als.default_alias_id
	LEFT JOIN bookbrainz.disambiguation dis ON dis.id = ad.disambiguation_id
	LEFT JOIN bookbrainz.author_type atype ON atype.id = ad.type_id
	WHERE e.type = 'Author';

CREATE OR REPLACE VIEW bookbrainz.edition AS
	SELECT
		e.bbid, edd.id AS data_id, edr.id AS revision_id, (edr.id = edh.master_revision_id) AS master, edd.annotation_id, edd.disambiguation_id, dis.comment disambiguation,
		als.default_alias_id, al."name", al.sort_name, edd.edition_group_bbid, edd.author_credit_id, edd.width, edd.height,
		edd.depth, edd.weight, edd.pages, edd.format_id, edd.status_id,
		edd.alias_set_id, edd.identifier_set_id, edd.relationship_set_id,
		edd.language_set_id, edd.release_event_set_id, edd.publisher_set_id, e.type
	FROM bookbrainz.edition_revision edr
	LEFT JOIN bookbrainz.entity e ON e.bbid = edr.bbid
	LEFT JOIN bookbrainz.edition_header edh ON edh.bbid = e.bbid
	LEFT JOIN bookbrainz.edition_data edd ON edr.data_id = edd.id
	LEFT JOIN bookbrainz.alias_set als ON edd.alias_set_id = als.id
	LEFT JOIN bookbrainz.alias al ON al.id = als.default_alias_id
	LEFT JOIN bookbrainz.disambiguation dis ON dis.id = edd.disambiguation_id
	WHERE e.type = 'Edition';

CREATE OR REPLACE VIEW bookbrainz.work AS
	SELECT
		e.bbid, wd.id AS data_id, wr.id AS revision_id, ( wr.id = wh.master_revision_id) AS master, wd.annotation_id, wd.disambiguation_id, dis.comment disambiguation,
		als.default_alias_id, al."name", al.sort_name, wd.type_id, worktype.label as work_type, wd.alias_set_id, wd.identifier_set_id,
		wd.relationship_set_id, wd.language_set_id, e.type
	FROM bookbrainz.work_revision wr
	LEFT JOIN bookbrainz.entity e ON e.bbid = wr.bbid
	LEFT JOIN bookbrainz.work_header wh ON wh.bbid = e.bbid
	LEFT JOIN bookbrainz.work_data wd ON wr.data_id = wd.id
	LEFT JOIN bookbrainz.alias_set als ON wd.alias_set_id = als.id
	LEFT JOIN bookbrainz.alias al ON al.id = als.default_alias_id
	LEFT JOIN bookbrainz.disambiguation dis ON dis.id = wd.disambiguation_id
	LEFT JOIN bookbrainz.work_type worktype ON worktype.id = wd.type_id
	WHERE e.type = 'Work';

CREATE OR REPLACE VIEW bookbrainz.publisher AS
	SELECT
		e.bbid, pubd.id AS data_id, psr.id AS revision_id, (psr.id = pubh.master_revision_id) AS master, pubd.annotation_id, pubd.disambiguation_id, dis.comment disambiguation,
		als.default_alias_id, al."name", al.sort_name, pubd.begin_year, pubd.begin_month, pubd.begin_day,
		pubd.end_year, pubd.end_month, pubd.end_day, pubd.ended, pubd.area_id,
		pubd.type_id, pubtype.label as publisher_type, pubd.alias_set_id, pubd.identifier_set_id, pubd.relationship_set_id, e.type
	FROM bookbrainz.publisher_revision psr
	LEFT JOIN bookbrainz.entity e ON e.bbid = psr.bbid
	LEFT JOIN bookbrainz.publisher_header pubh ON pubh.bbid = e.bbid
	LEFT JOIN bookbrainz.publisher_data pubd ON psr.data_id = pubd.id
	LEFT JOIN bookbrainz.alias_set als ON pubd.alias_set_id = als.id
	LEFT JOIN bookbrainz.alias al ON al.id = als.default_alias_id
	LEFT JOIN bookbrainz.disambiguation dis ON dis.id = pubd.disambiguation_id
	LEFT JOIN bookbrainz.publisher_type pubtype ON pubtype.id = pubd.type_id
	WHERE e.type = 'Publisher';

CREATE OR REPLACE VIEW bookbrainz.edition_group AS
	SELECT
		e.bbid, egd.id AS data_id, pcr.id AS revision_id, (pcr.id = egh.master_revision_id) AS master, egd.annotation_id, egd.disambiguation_id, dis.comment disambiguation,
		als.default_alias_id, al."name", al.sort_name, egd.type_id, egtype.label as edition_group_type, egd.author_credit_id, egd.alias_set_id, egd.identifier_set_id,
		egd.relationship_set_id, e.type
	FROM bookbrainz.edition_group_revision pcr
	LEFT JOIN bookbrainz.entity e ON e.bbid = pcr.bbid
	LEFT JOIN bookbrainz.edition_group_header egh ON egh.bbid = e.bbid
	LEFT JOIN bookbrainz.edition_group_data egd ON pcr.data_id = egd.id
	LEFT JOIN bookbrainz.alias_set als ON egd.alias_set_id = als.id
	LEFT JOIN bookbrainz.alias al ON al.id = als.default_alias_id
	LEFT JOIN bookbrainz.disambiguation dis ON dis.id = egd.disambiguation_id
	LEFT JOIN bookbrainz.edition_group_type egtype ON egtype.id = egd.type_id
	WHERE e.type = 'EditionGroup';

CREATE OR REPLACE VIEW bookbrainz.series AS
	SELECT
		e.bbid, sd.id AS data_id, sr.id AS revision_id, (sr.id = sh.master_revision_id) AS master, sd.entity_type, sd.annotation_id, sd.disambiguation_id, dis.comment disambiguation,
		als.default_alias_id, al."name", al.sort_name, sd.ordering_type_id, sd.alias_set_id, sd.identifier_set_id,
		sd.relationship_set_id, e.type
	FROM bookbrainz.series_revision sr
	LEFT JOIN bookbrainz.entity e ON e.bbid = sr.bbid
	LEFT JOIN bookbrainz.series_header sh ON sh.bbid = e.bbid
	LEFT JOIN bookbrainz.series_data sd ON sr.data_id = sd.id
	LEFT JOIN bookbrainz.alias_set als ON sd.alias_set_id = als.id
	LEFT JOIN bookbrainz.alias al ON al.id = als.default_alias_id
	LEFT JOIN bookbrainz.disambiguation dis ON dis.id = sd.disambiguation_id
	WHERE e.type = 'Series';


COMMIT;


CREATE OR REPLACE FUNCTION bookbrainz.process_author() RETURNS TRIGGER
	AS $process_author$
	DECLARE
		author_data_id INT;
	BEGIN
		IF (TG_OP = 'INSERT') THEN
			INSERT INTO bookbrainz.author_header(bbid) VALUES(NEW.bbid);
		END IF;

		IF (NEW.ended IS NULL) THEN
			NEW.ended = false;
		END IF;

		-- If we're not deleting, create new entity data rows as necessary
		IF (TG_OP <> 'DELETE') THEN
			INSERT INTO bookbrainz.author_data(
				alias_set_id, identifier_set_id, relationship_set_id, annotation_id,
				disambiguation_id, begin_year, begin_month, begin_day, begin_area_id,
				end_year, end_month, end_day, end_area_id, ended, area_id, gender_id,
				type_id
			) VALUES (
				NEW.alias_set_id, NEW.identifier_set_id, NEW.relationship_set_id,
				NEW.annotation_id, NEW.disambiguation_id, NEW.begin_year,
				NEW.begin_month, NEW.begin_day, NEW.begin_area_id, NEW.end_year,
				NEW.end_month, NEW.end_day, NEW.end_area_id, NEW.ended, NEW.area_id, NEW.gender_id,
				NEW.type_id
			) RETURNING bookbrainz.author_data.id INTO author_data_id;

			INSERT INTO bookbrainz.author_revision VALUES(NEW.revision_id, NEW.bbid, author_data_id);
		ELSE
			INSERT INTO bookbrainz.author_revision VALUES(NEW.revision_id, NEW.bbid, NULL);
		END IF;

		UPDATE bookbrainz.author_header
			SET master_revision_id = NEW.revision_id
			WHERE bbid = NEW.bbid;

		IF (TG_OP = 'DELETE') THEN
			RETURN OLD;
		ELSE
			RETURN NEW;
		END IF;
	END;
$process_author$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION bookbrainz.process_edition() RETURNS TRIGGER
	AS $process_edition$
	DECLARE
		edition_data_id INT;
	BEGIN
		IF (TG_OP = 'INSERT') THEN
			INSERT INTO bookbrainz.edition_header(bbid) VALUES(NEW.bbid);
		END IF;

		-- If we're not deleting, create new entity data rows as necessary
		IF (TG_OP <> 'DELETE') THEN
			INSERT INTO bookbrainz.edition_data(
				alias_set_id, identifier_set_id, relationship_set_id, annotation_id,
				disambiguation_id, edition_group_bbid, author_credit_id,
				publisher_set_id, release_event_set_id, language_set_id, width,
				height, depth, weight, pages, format_id, status_id
			) VALUES (
				NEW.alias_set_id, NEW.identifier_set_id, NEW.relationship_set_id,
				NEW.annotation_id, NEW.disambiguation_id, NEW.edition_group_bbid,
				NEW.author_credit_id, NEW.publisher_set_id,
				NEW.release_event_set_id, NEW.language_set_id, NEW.width,
				NEW.height, NEW.depth, NEW.weight, NEW.pages, NEW.format_id,
				NEW.status_id
			) RETURNING bookbrainz.edition_data.id INTO edition_data_id;

			INSERT INTO bookbrainz.edition_revision VALUES(NEW.revision_id, NEW.bbid, edition_data_id);
		ELSE
			INSERT INTO bookbrainz.edition_revision VALUES(NEW.revision_id, NEW.bbid, NULL);
		END IF;

		UPDATE bookbrainz.edition_header
			SET master_revision_id = NEW.revision_id
			WHERE bbid = NEW.bbid;

		IF (TG_OP = 'DELETE') THEN
			RETURN OLD;
		ELSE
			RETURN NEW;
		END IF;
	END;
$process_edition$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION bookbrainz.process_series() RETURNS TRIGGER
	AS $process_series$
	DECLARE
		series_data_id INT;
	BEGIN
		IF (TG_OP = 'INSERT') THEN
			INSERT INTO bookbrainz.series_header(bbid) VALUES(NEW.bbid);
		END IF;

		-- If we're not deleting, create new entity data rows as necessary
		IF (TG_OP <> 'DELETE') THEN
			INSERT INTO bookbrainz.series_data(
				alias_set_id, identifier_set_id, relationship_set_id, annotation_id,
				disambiguation_id, entity_type, ordering_type_id
			) VALUES (
				NEW.alias_set_id, NEW.identifier_set_id, NEW.relationship_set_id,
				NEW.annotation_id, NEW.disambiguation_id,
				NEW.entity_type, NEW.ordering_type_id
			) RETURNING bookbrainz.series_data.id INTO series_data_id;

			INSERT INTO bookbrainz.series_revision VALUES(NEW.revision_id, NEW.bbid, series_data_id);
		ELSE
			INSERT INTO bookbrainz.series_revision VALUES(NEW.revision_id, NEW.bbid, NULL);
		END IF;

		UPDATE bookbrainz.series_header
			SET master_revision_id = NEW.revision_id
			WHERE bbid = NEW.bbid;

		IF (TG_OP = 'DELETE') THEN
			RETURN OLD;
		ELSE
			RETURN NEW;
		END IF;
	END;
$process_series$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION bookbrainz.process_work() RETURNS TRIGGER
	AS $process_work$
	DECLARE
		work_data_id INT;
	BEGIN
		IF (TG_OP = 'INSERT') THEN
			INSERT INTO bookbrainz.work_header(bbid) VALUES(NEW.bbid);
		END IF;

		-- If we're not deleting, create new entity data rows as necessary
		IF (TG_OP <> 'DELETE') THEN
			INSERT INTO bookbrainz.work_data(
				alias_set_id, identifier_set_id, relationship_set_id, annotation_id,
				disambiguation_id, language_set_id, type_id
			) VALUES (
				NEW.alias_set_id, NEW.identifier_set_id, NEW.relationship_set_id,
				NEW.annotation_id, NEW.disambiguation_id, NEW.language_set_id,
				NEW.type_id
			) RETURNING bookbrainz.work_data.id INTO work_data_id;

			INSERT INTO bookbrainz.work_revision VALUES(NEW.revision_id, NEW.bbid, work_data_id);
		ELSE
			INSERT INTO bookbrainz.work_revision VALUES(NEW.revision_id, NEW.bbid, NULL);
		END IF;

		UPDATE bookbrainz.work_header
			SET master_revision_id = NEW.revision_id
			WHERE bbid = NEW.bbid;

		IF (TG_OP = 'DELETE') THEN
			RETURN OLD;
		ELSE
			RETURN NEW;
		END IF;
	END;
$process_work$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION bookbrainz.process_publisher() RETURNS TRIGGER
	AS $process_publisher$
	DECLARE
		publisher_data_id INT;
	BEGIN
		IF (TG_OP = 'INSERT') THEN
			INSERT INTO bookbrainz.publisher_header(bbid) VALUES(NEW.bbid);
		END IF;

		IF (NEW.ended IS NULL) THEN
			NEW.ended = false;
		END IF;

		-- If we're not deleting, create new entity data rows as necessary
		IF (TG_OP <> 'DELETE') THEN
			INSERT INTO bookbrainz.publisher_data(
				alias_set_id, identifier_set_id, relationship_set_id, annotation_id,
				disambiguation_id, type_id, begin_year, begin_month, begin_day, end_year,
				end_month, end_day, ended, area_id
			) VALUES (
				NEW.alias_set_id, NEW.identifier_set_id, NEW.relationship_set_id,
				NEW.annotation_id, NEW.disambiguation_id, NEW.type_id, NEW.begin_year,
				NEW.begin_month, NEW.begin_day, NEW.end_year, NEW.end_month, NEW.end_day,
				NEW.ended, NEW.area_id
			) RETURNING bookbrainz.publisher_data.id INTO publisher_data_id;

			INSERT INTO bookbrainz.publisher_revision VALUES(NEW.revision_id, NEW.bbid, publisher_data_id);
		ELSE
			INSERT INTO bookbrainz.publisher_revision VALUES(NEW.revision_id, NEW.bbid, NULL);
		END IF;

		UPDATE bookbrainz.publisher_header
			SET master_revision_id = NEW.revision_id
			WHERE bbid = NEW.bbid;

		IF (TG_OP = 'DELETE') THEN
			RETURN OLD;
		ELSE
			RETURN NEW;
		END IF;
	END;
$process_publisher$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION bookbrainz.process_edition_group() RETURNS TRIGGER
	AS $process_edition_group$
	DECLARE
		edition_group_data_id INT;
	BEGIN
		IF (TG_OP = 'INSERT') THEN
			INSERT INTO bookbrainz.edition_group_header(bbid) VALUES(NEW.bbid);
		END IF;

		-- If we're not deleting, create new entity data rows as necessary
		IF (TG_OP <> 'DELETE') THEN
			INSERT INTO bookbrainz.edition_group_data(
				alias_set_id, identifier_set_id, relationship_set_id, annotation_id,
				disambiguation_id, type_id, author_credit_id
			) VALUES (
				NEW.alias_set_id, NEW.identifier_set_id, NEW.relationship_set_id,
				NEW.annotation_id, NEW.disambiguation_id, NEW.type_id, NEW.author_credit_id
			) RETURNING bookbrainz.edition_group_data.id INTO edition_group_data_id;

			INSERT INTO bookbrainz.edition_group_revision VALUES(NEW.revision_id, NEW.bbid, edition_group_data_id);
		ELSE
			INSERT INTO bookbrainz.edition_group_revision VALUES(NEW.revision_id, NEW.bbid, NULL);
		END IF;

		UPDATE bookbrainz.edition_group_header
			SET master_revision_id = NEW.revision_id
			WHERE bbid = NEW.bbid;

		IF (TG_OP = 'DELETE') THEN
			RETURN OLD;
		ELSE
			RETURN NEW;
		END IF;
	END;
$process_edition_group$ LANGUAGE plpgsql;


BEGIN;

CREATE TRIGGER process_author
	INSTEAD OF INSERT OR UPDATE OR DELETE ON bookbrainz.author
	FOR EACH ROW EXECUTE PROCEDURE bookbrainz.process_author();

COMMIT;

BEGIN;

CREATE TRIGGER process_edition
	INSTEAD OF INSERT OR UPDATE OR DELETE ON bookbrainz.edition
	FOR EACH ROW EXECUTE PROCEDURE bookbrainz.process_edition();

COMMIT;

BEGIN;

CREATE TRIGGER process_series
	INSTEAD OF INSERT OR UPDATE OR DELETE ON bookbrainz.series
	FOR EACH ROW EXECUTE PROCEDURE bookbrainz.process_series();

COMMIT;

BEGIN;

CREATE TRIGGER process_work
	INSTEAD OF INSERT OR UPDATE OR DELETE ON bookbrainz.work
	FOR EACH ROW EXECUTE PROCEDURE bookbrainz.process_work();

COMMIT;

BEGIN;

CREATE TRIGGER process_publisher
	INSTEAD OF INSERT OR UPDATE OR DELETE ON bookbrainz.publisher
	FOR EACH ROW EXECUTE PROCEDURE bookbrainz.process_publisher();

COMMIT;

BEGIN;

CREATE TRIGGER process_edition_group
	INSTEAD OF INSERT OR UPDATE OR DELETE ON bookbrainz.edition_group
	FOR EACH ROW EXECUTE PROCEDURE bookbrainz.process_edition_group();

COMMIT;

BEGIN TRANSACTION;
UPDATE bookbrainz.identifier_type
SET display_template =
	CASE
		WHEN id = 1 THEN 'https://musicbrainz.org/release/{value}'
		WHEN id = 2 THEN 'https://musicbrainz.org/artist/{value}'
		WHEN id = 3 THEN 'https://musicbrainz.org/work/{value}'
		WHEN id = 4 THEN 'https://www.wikidata.org/wiki/{value}'
		WHEN id = 5 THEN 'https://www.amazon.com/dp/{value}'
		WHEN id = 6 THEN 'https://openlibrary.org/books/{value}'
		WHEN id = 8 THEN 'https://openlibrary.org/works/{value}'
		WHEN id = 9 THEN 'https://isbnsearch.org/isbn/{value}'
		WHEN id = 10 THEN 'https://isbnsearch.org/isbn/{value}'
		WHEN id = 11 THEN 'https://www.barcodelookup.com/{value}'
		WHEN id = 13 THEN 'http://www.isni.org/{value}'
		WHEN id = 14 THEN 'https://www.librarything.com/work/{value}'
		WHEN id = 15 THEN 'https://www.librarything.com/author/{value}'
		WHEN id = 16 THEN 'https://www.imdb.com/title/{value}'
		WHEN id = 17 THEN 'https://musicbrainz.org/label/{value}'
		WHEN id = 22 THEN 'https://www.archive.org/details/{value}'
		WHEN id = 23 THEN 'https://www.openlibrary.org/authors/{value}'
		WHEN id = 24 THEN 'https://lccn.loc.gov/{value}'
		WHEN id = 25 THEN 'https://www.orcid.org/{value}'
		WHEN id = 26 THEN 'https://www.worldcat.org/oclc/{value}'
		WHEN id = 27 THEN 'https://www.goodreads.com/author/show/{value}'
		WHEN id = 28 THEN 'https://www.goodreads.com/book/show/{value}'
		WHEN id = 32 THEN 'https://musicbrainz.org/series/{value}'
		WHEN id = 33 THEN 'https://www.goodreads.com/series/{value}'
		WHEN id = 34 THEN 'https://www.imdb.com/list/{value}'
		WHEN id in (12, 29, 31) THEN 'https://viaf.org/viaf/{value}'
		WHEN id in (18, 19, 20, 21, 30) THEN 'https://www.wikidata.org/wiki/{value}'
	END
WHERE id IN (1,2,3,4,5,6,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34);

COMMIT;