import os
import tempfile
from functools import wraps
from datetime import datetime
from click.testing import CliRunner
from critiquebrainz.data.testing import DataTestCase
from critiquebrainz.frontend import create_app
from critiquebrainz.data import utils
import critiquebrainz.db.license as db_license
import critiquebrainz.db.users as db_users
import critiquebrainz.db.review as db_review
from critiquebrainz.db.user import User


def with_test_request_context(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        print("HERE IN TEST REQUEST CONTEXT")
        with create_app(
            config_path=os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                '..', 'test_config.py')).test_request_context():

            return f(*args, **kwargs)
    return decorated


utils.with_request_context = with_test_request_context
from critiquebrainz.data import dump_manager  # pylint: disable=wrong-import-position


def get_archives(root_dir):
    archives = {}
    for roots, dirs, files in os.walk(root_dir):  # pylint: disable=unused-variable
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
        user = User(db_users.get_or_create("Tester", new_user_data={
            "display_name": "test user",
        }))
        db_review.create(
            user_id=user.id,
            entity_id="e7aad618-fa86-3983-9e77-405e21796eca",
            entity_type="release_group",
            text="Testing",
            rating=5,
            is_draft=False,
            license_id=self.license["id"],
        )

        # Make dumps and reset db
        self.runner.invoke(dump_manager.public, ['--location', self.tempdir])
        archives = get_archives(self.tempdir)
        # self.reset_db()

        # Import dumps - cbdump.tar.bz2 and cbdump-reviews-all.tar.bz2 and check if data imported properly
        self.runner.invoke(dump_manager.importer, [archives['cbdump.tar.bz2']])
        self.assertEqual(db_users.total_count(), 1)

        self.runner.invoke(dump_manager.importer, [archives['cbdump-reviews-all.tar.bz2']])
        self.assertEqual(db_review.get_count(), 1)
