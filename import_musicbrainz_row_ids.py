from critiquebrainz.frontend.external import musicbrainz_db
from critiquebrainz.frontend import create_app
from critiquebrainz import db
from sqlalchemy import text

import critiquebrainz.db.users as db_users

def fix_exceptions():
    pass


def import_musicbrainz_row_ids(dry_run=True):
    fix_exceptions()
    import_count = 0
    already_imported = 0
    deleted = 0
    not_found = 0

    all_users = db_users.list_users()
    musicbrainz_users = [x for x in all_users if x['musicbrainz_username'] is not None]
    with musicbrainz_db.engine.connect() as mb_connection:
        with db.engine.connect() as connection:
            for user in musicbrainz_users:
                if user.get('musicbrainz_row_id') is not None:
                    already_imported += 1
                    continue

                name = user.get('musicbrainz_username')
                r = mb_connection.execute(text("""
                    SELECT id
                      FROM editor
                     WHERE name = :musicbrainz_id
                    """), {
                        'musicbrainz_id': user['musicbrainz_username'],
                    })
                musicbrainz_row_id = None
                if r.rowcount > 0:
                    musicbrainz_row_id = r.fetchone()['id']
                    print('found %s - %s!!!!!!!!!!!!!!!!!!!' % (name, musicbrainz_row_id))
                    import_count += 1
                    if not dry_run:
                        connection.execute(text("""
                            UPDATE "user"
                               SET musicbrainz_row_id = :musicbrainz_row_id
                             WHERE id = :id
                            """), {
                                'musicbrainz_row_id': musicbrainz_row_id,
                                'id': user['id'],
                            })
                else:
                    print('%s not found!' %  name)
                    not_found += 1;
                    if not dry_run:
                        print('Deleting user %s' % user['musicbrainz_username'])
                        db_users.delete(user['id'])
                        deleted += 1

    print('Total number of CB users: %d' % len(all_users))
    print('Total number of CB users with MusicBrainz usernames: %d' % len(musicbrainz_users))
    print('Total number of CB users with already imported row IDs: %d' % already_imported)
    print('Total number of CB users with row IDs that can be imported: %d' % import_count)
    print('Total number of CB users not found and deleted: %d' % not_found)


def main(dry_run=True):
    app = create_app()
    with app.app_context():
        import_musicbrainz_row_ids(dry_run=False)


if __name__ == '__main__':
    main()
