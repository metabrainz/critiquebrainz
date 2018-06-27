from datetime import datetime, date, timedelta
from uuid import UUID
from critiquebrainz.data.testing import DataTestCase
import critiquebrainz.db.users as db_users
from critiquebrainz.db.users import gravatar_url, get_many_by_mb_username
import critiquebrainz.db.review as db_review
import critiquebrainz.db.spam_report as db_spam_report
import critiquebrainz.db.vote as db_vote
import critiquebrainz.db.license as db_license
import critiquebrainz.db.oauth_client as db_oauth_client
import critiquebrainz.db.oauth_token as db_oauth_token
from critiquebrainz.db.user import User


class UserTestCase(DataTestCase):
    def setUp(self):
        super(UserTestCase, self).setUp()
        self.user1 = User(db_users.get_or_create('tester_1', new_user_data={
            "display_name": "test",
        }))
        self.user2 = User(db_users.get_or_create("тестер", new_user_data={
            "display_name": "test1",
        }))
        self.author = User(db_users.get_or_create("author1", new_user_data={
            "display_name": "Author1",
        }))
        license = db_license.create(
            id='Test',
            full_name='Test License',
        )
        self.review = db_review.create(
            entity_id="e7aad618-fa86-3983-9e77-405e21796eca",
            entity_type="release_group",
            text="Testing!",
            user_id=self.author.id,
            is_draft=False,
            license_id=license["id"],
        )
        db_vote.submit(self.user1.id, self.review["last_revision"]["id"], True)
        self.review_created = self.review["last_revision"]["timestamp"]
        self.review_id = self.review["id"]
        self.revision_id = self.review["last_revision"]["id"]
        self.report = db_spam_report.create(self.revision_id, self.user1.id, "Testing Reason Report")

    def test_get_many_by_mb_username(self):
        users = [self.user1.musicbrainz_username, self.user2.musicbrainz_username]
        dbresults = get_many_by_mb_username(users)
        dbresults = [user["musicbrainz_username"] for user in dbresults]
        self.assertEqual(users, dbresults)
        self.assertEqual(get_many_by_mb_username([]), [])

    def test_avatar(self):
        self.assertEqual(
            gravatar_url("test2"),
            "https://gravatar.com/avatar/ad0234829205b9033196ba818f7a872b?d=identicon&r=pg"
        )

    def test_get_by_id(self):
        user = db_users.get_by_id(self.user1.id)
        self.assertEqual(user['display_name'], "test")
        self.assertEqual(user['musicbrainz_username'], "tester_1")

    def test_users_list_users(self):
        users = db_users.list_users()
        self.assertEqual(len(users), 3)

        users = db_users.list_users(0, 10)
        self.assertEqual(len(users), 0)

        db_users.get_or_create("user_1", new_user_data={
            "display_name": "test2",
        })
        users = db_users.list_users(1, 1)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]['display_name'], "test1")

    def test_total_count(self):
        count = db_users.total_count()
        self.assertEqual(count, 3)

        db_users.get_or_create("user1", new_user_data={
            "display_name": "user_1",
        })
        count = db_users.total_count()
        self.assertEqual(count, 4)

    def test_get_by_mbid(self):
        user = db_users.get_by_mbid("tester_1")
        self.assertEqual(user['display_name'], "test")

    def test_create(self):
        user = db_users.create(display_name="test_user", email="foo@foo.com", musicbrainz_username="tester2")
        self.assertEqual(user['email'], "foo@foo.com")
        self.assertEqual(type(user['id']), UUID)
        self.assertEqual(user['is_blocked'], False)

    def test_vote(self):
        voted = db_users.has_voted(self.user1.id, self.review["id"])
        self.assertEqual(voted, True)
        voted = db_users.has_voted(self.user2.id, self.review["id"])
        self.assertEqual(voted, False)

    def test_karma(self):
        karma = db_users.karma(self.author.id)
        self.assertEqual(karma, 1)
        karma = db_users.karma(self.user2.id)
        self.assertEqual(karma, 0)

    def test_reviews(self):
        review = db_users.reviews(self.author.id)[0]
        self.assertEqual(review['license_id'], 'Test')
        self.assertEqual(type(review['user_id']), UUID)
        self.assertEqual(str(review['user_id']), self.author.id)

    def test_get_votes(self):
        votes = db_users.get_votes(self.user1.id)
        self.assertEqual(len(votes), 1)
        two_days_from_now = date.today() + timedelta(days=2)
        votes = db_users.get_votes(self.user1.id, from_date=two_days_from_now)
        self.assertEqual(len(votes), 0)

    def test_get_reviews(self):
        reviews = db_users.get_reviews(self.author.id)
        self.assertEqual(len(reviews), 1)
        db_review.update(
            review_id=self.review["id"],
            drafted=self.review["is_draft"],
            text="Testing Again",
        )
        reviews = db_users.get_reviews(self.author.id)
        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0]['creation_time'], self.review_created)
        two_days_from_now = date.today() + timedelta(days=2)
        reviews = db_users.get_reviews(self.author.id, from_date=two_days_from_now)
        self.assertEqual(len(reviews), 0)

    def test_update(self):
        db_users.update(self.user1.id, user_new_info={
            "email": 'foo@foo.com',
        })
        user1 = db_users.get_by_id(self.user1.id)
        self.assertEqual(user1['email'], 'foo@foo.com')

    def test_delete(self):

        user1_id = self.user1.id
        db_users.delete(self.user1.id)
        # Votes should be deleted as well
        votes = db_users.get_votes(self.user1.id)
        self.assertEqual(len(votes), 0)
        # Spam Reports to be deleted as well
        spam_reports, count = db_spam_report.list_reports(user_id=user1_id)  # pylint: disable=unused-variable
        self.assertEqual(count, 0)

        db_users.delete(self.author.id)
        # Review should not exist
        reviews = db_users.get_reviews(self.author.id)
        self.assertEqual(len(reviews), 0)

    def test_user_clients(self):
        db_oauth_client.create(
            user_id=self.user1.id,
            name="Some Application",
            desc="Created for some purpose",
            website="https://example.com",
            redirect_uri="https://example.com/redirect/",
        )
        client = db_users.clients(self.user1.id)[0]
        self.assertEqual(client["name"], "Some Application")
        self.assertEqual(client["website"], "https://example.com")

    def test_user_tests(self):
        db_oauth_client.create(
            user_id=self.user1.id,
            name="Some Application",
            desc="Created for some purpose",
            website="https://example.com",
            redirect_uri="https://example.com/redirect/",
        )
        client = db_users.clients(self.user1.id)[0]
        db_oauth_token.create(
            client_id=client["client_id"],
            access_token="Test Access Token",
            refresh_token="Test Refresh Token",
            expires=datetime.now() + timedelta(seconds=200),
            user_id=self.user1.id,
            scopes=None,
        )
        tokens = db_users.tokens(self.user1.id)
        self.assertEqual(tokens[0]["client_name"], "Some Application")
        self.assertEqual(tokens[0]["refresh_token"], "Test Refresh Token")
