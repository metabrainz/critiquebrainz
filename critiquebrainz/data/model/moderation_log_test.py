from critiquebrainz.data.testing import DataTestCase
from critiquebrainz.data import db
from critiquebrainz.data.model.user import User
from critiquebrainz.data.model.license import License
from critiquebrainz.data.model.review import Review
from critiquebrainz.data.model.moderation_log import (
    ModerationLog,
    ACTION_HIDE_REVIEW,
    ACTION_BLOCK_USER,
)


class ModerationLogCase(DataTestCase):

    def setUp(self):
        super(ModerationLogCase, self).setUp()

        self.admin = User(display_name=u'Admin')
        db.session.add(self.admin)

        self.user = User(display_name=u'User')
        db.session.add(self.user)

        self.reason = "Testing Reason"

        self.license = License(id=u'Test', full_name=u'Test License')
        db.session.add(self.license)
        db.session.flush()

        self.review = Review.create(user_id=self.user.id, release_group='e7aad618-fa86-3983-9e77-405e21796eca',
                                    text=u"It's... beautiful!", is_draft=False, license_id=self.license.id,
                                    language='en')

    def test_log_creation(self):
        self.assertEqual(ModerationLog.query.count(), 0)

        log = ModerationLog.create(admin_id=self.admin.id, reason=self.reason,
                                   action=ACTION_BLOCK_USER, user_id=self.user.id)

        all_logs = ModerationLog.query.all()
        self.assertEqual(len(all_logs), 1)
        self.assertEqual(all_logs[0].user_id, log.user_id)
        self.assertEqual(all_logs[0].reason, log.reason)

    def test_log_deletion(self):
        log = ModerationLog.create(admin_id=self.admin.id, reason=self.reason,
                                   action=ACTION_HIDE_REVIEW, review_id=self.review.id)
        self.assertEqual(ModerationLog.query.count(), 1)

        log.delete()
        self.assertEqual(ModerationLog.query.count(), 0)
