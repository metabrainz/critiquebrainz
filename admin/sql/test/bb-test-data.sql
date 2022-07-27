-- Sample Data for testing relationships between entities

INSERT INTO relationship (id, type_id,source_bbid, target_bbid)
     VALUES (99999999,
             8,
             'e5c4e68b-bfce-4c77-9ca2-0f0a2d4d09f0',
             '9f49df73-8ee5-4c5f-8803-427c9b216d8f');

INSERT INTO relationship_set (id) VALUES (99999999);

INSERT INTO relationship_set__relationship (set_id, relationship_id) 
     VALUES (99999999,
            99999999);


-- Sample Data for testing author credits for edition groups

UPDATE edition_group_data
   SET author_credit_id = NULL
  FROM edition_group_revision as egr, edition_group_header as egh
 WHERE egr.data_id = edition_group_data.id
   AND egh.master_revision_id = egr.id
   AND egh.bbid = 'fd84cf1f-b288-4ea2-8e05-41257764fa6b';


INSERT INTO author_credit (id, author_count, ref_count)
     VALUES (99999999,
            1,
            0);


INSERT INTO author_credit_name (author_credit_id, position, author_bbid, name, join_phrase )
    VALUES (99999999,
            0,
            'e5c4e68b-bfce-4c77-9ca2-0f0a2d4d09f0',
            'Test Author',
            'Test Join Phrase');


UPDATE edition_group_data
   SET author_credit_id = 99999999
  FROM edition_group_revision as egr, edition_group_header as egh
 WHERE egr.data_id = edition_group_data.id
   AND egh.master_revision_id = egr.id
   AND egh.bbid = '9f49df73-8ee5-4c5f-8803-427c9b216d8f';
