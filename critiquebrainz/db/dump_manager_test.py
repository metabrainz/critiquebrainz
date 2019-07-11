import os
import tempfile
from datetime import datetime
from click.testing import CliRunner
from critiquebrainz.data.testing import DataTestCase
from critiquebrainz.data import utils
import critiquebrainz.db.license as db_license
import critiquebrainz.db.users as db_users
import critiquebrainz.db.review as db_review
import critiquebrainz.db.vote as db_vote
from critiquebrainz.db.user import User

utils.with_request_context = utils.with_test_request_context  # noqa
from critiquebrainz.data import dump_manager  # pylint:disable=wrong-import-position


def get_archives(root_dir):
    """Returns a dictionary of bz2 archives and their respective paths.

    Args:
        root_dir: Path of the root dir.
    Returns:
        Dictionary with the following structure:
        {
            archive_name: archive_path
        }
    """
    archives = {}
    for roots, _, files in os.walk(root_dir):
        for f in files:
            if f.endswith('tar.bz2'):
                archives[f] = os.path.join(roots, f)
    return archives


class DumpManagerTestCase(DataTestCase):

    def setUp(self):
        super().setUp()
        self.tempdir = tempfile.mkdtemp()
        self.runner = CliRunner()
        self.license = db_license.create(
            id=u'test',
            full_name=u"Test License",
        )

    def test_full_db(self):
        self.runner.invoke(dump_manager.full_db, ['--location', self.tempdir])
        self.assertTrue(os.listdir(self.tempdir)[0].endswith('.tar.bz2'))

    def test_json_dumps(self):
        date = datetime.today().strftime('%Y%m%d')
        self.runner.invoke(dump_manager.json, ['--location', self.tempdir])
        self.assertIn(f'critiquebrainz-{date}-{self.license["id"]}-json.tar.bz2', os.listdir(self.tempdir))

    def test_public(self):
        self.runner.invoke(dump_manager.public, ['--location', self.tempdir])
        archives = get_archives(self.tempdir).keys()
        self.assertIn('cbdump.tar.bz2', archives)
        self.assertIn('cbdump-reviews-all.tar.bz2', archives)
        self.assertIn(f'cbdump-reviews-{self.license["id"]}.tar.bz2', archives)

    def test_importer(self):
        user_1 = User(db_users.get_or_create(1, "Tester_1", new_user_data={
            "display_name": "test user_1",
        }))
        user_2 = User(db_users.get_or_create(2, "Tester_2", new_user_data={
            "display_name": "test user_2",
        }))

        # user_1 adds a review
        review = db_review.create(
            user_id=user_1.id,
            entity_id="e7aad618-fa86-3983-9e77-405e21796eca",
            entity_type="release_group",
            text="Testing",
            rating=5,
            is_draft=False,
            license_id=self.license["id"],
        )
        # user_2 votes on review by user_1
        db_vote.submit(user_2.id, review["last_revision"]["id"], True)

        # Make dumps and delete entities
        self.runner.invoke(dump_manager.public, ['--location', self.tempdir])
        archives = get_archives(self.tempdir)
        db_review.delete(review['id'])
        db_users.delete(user_1.id)
        db_users.delete(user_2.id)
        self.assertEqual(db_users.total_count(), 0)
        self.assertEqual(db_review.get_count(), 0)
        self.assertEqual(db_vote.get_count(), 0)

        # Import dumps - cbdump.tar.bz2 and cbdump-reviews-all.tar.bz2 and check if data imported properly
        self.runner.invoke(dump_manager.importer, [archives['cbdump.tar.bz2']])
        self.assertEqual(db_users.total_count(), 2)

        self.runner.invoke(dump_manager.importer, [archives['cbdump-reviews-all.tar.bz2']])
        self.assertEqual(db_review.get_count(), 1)
        self.assertEqual(db_vote.get_count(), 1)
