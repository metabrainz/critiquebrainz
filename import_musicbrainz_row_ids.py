from sqlalchemy import text
from brainzutils import musicbrainz_db
import critiquebrainz.db.users as db_users
from critiquebrainz.frontend import create_app
from critiquebrainz import db

DRY_RUN = True


def fix_user(mb_connection, cb_connection, user_name, cb_id):
    r = mb_connection.execute(text("""
            SELECT id
              FROM editor
             WHERE name = :user_name
        """), {
        'user_name': user_name,
    })
    if r.rowcount > 0:
        musicbrainz_row_id = r.fetchone()['id']
        if not DRY_RUN:
            cb_connection.execute(text("""
                UPDATE "user"
                   SET musicbrainz_row_id = :musicbrainz_row_id
                 WHERE id = :id
            """), {
                'musicbrainz_row_id': musicbrainz_row_id,
                'id': cb_id,
            })


def fix_exceptions():
    with musicbrainz_db.engine.connect() as mb_connection:
        with db.engine.connect() as connection:
            fix_user(mb_connection, connection, 'Per Starbäck', '47ba9a3e-f0a7-404e-a192-105dd0a6ba9f')
            fix_user(mb_connection, connection, 'CallerNo6', '7cfb9660-b007-4a03-84cb-45f13841ddf3')
            fix_user(mb_connection, connection, 'OphélieN', '27f56372-0c07-45e2-a13e-7709fd796fb2')
            fix_user(mb_connection, connection, 'Sombréro', '813a7571-12ef-402b-af9d-2b258e5008be')
            fix_user(mb_connection, connection, 'Véronique', 'c8120f45-b00e-423b-a04a-5213f9948d4e')
            fix_user(mb_connection, connection, 'jflory', '1f760ce8-468d-4480-9382-802cad732498 ')
            fix_user(mb_connection, connection, 'ágarsenó', '53017bc2-6f2e-48ca-9b76-5fd512a3210d')
            fix_user(mb_connection, connection, 'ClæpsHydra', 'aea092b6-eef6-4e95-a9f8-29ccd2832a2b')


def import_musicbrainz_row_ids():
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
                    if not DRY_RUN:
                        connection.execute(text("""
                            UPDATE "user"
                               SET musicbrainz_row_id = :musicbrainz_row_id
                             WHERE id = :id
                            """), {
                            'musicbrainz_row_id': musicbrainz_row_id,
                            'id': user['id'],
                        })
                else:
                    print('%s not found!' % name)
                    not_found += 1
                    if not DRY_RUN:
                        print('Deleting user %s' % user['musicbrainz_username'])
                        db_users.delete(user['id'])
                        deleted += 1

    print('Total number of CB users: %d' % len(all_users))
    print('Total number of CB users with MusicBrainz usernames: %d' % len(musicbrainz_users))
    print('Total number of CB users with already imported row IDs: %d' % already_imported)
    print('Total number of CB users with row IDs that can be imported: %d' % import_count)
    print('Total number of CB users not found and deleted: %d' % not_found)


def main():
    app = create_app()
    with app.app_context():
        import_musicbrainz_row_ids()


if __name__ == '__main__':
    # make sure you set DRY_RUN before running this
    main()
