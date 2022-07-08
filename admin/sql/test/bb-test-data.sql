INSERT INTO relationship (id, type_id,source_bbid, target_bbid)
     VALUES (99999999,
             8,
             'e5c4e68b-bfce-4c77-9ca2-0f0a2d4d09f0',
             '9f49df73-8ee5-4c5f-8803-427c9b216d8f');

INSERT INTO relationship_set (id) VALUES (99999999);

INSERT INTO relationship_set__relationship (set_id, relationship_id) 
     VALUES (99999999,
            99999999);
