from critiquebrainz.data.testing import DataTestCase
from critiquebrainz.data import db
from critiquebrainz.data.model.vote import Vote
from critiquebrainz.data.model.user import User
from critiquebrainz.data.model.review import Review
from critiquebrainz.data.model.license import License


class VoteTestCase(DataTestCase):

    def test_vote_create(self):
        # Preparing test data
        author = User.get_or_create(u'Author', musicbrainz_id=u'0')
        user_1 = User.get_or_create(u'Tester #1', musicbrainz_id=u'1')
        user_2 = User.get_or_create(u'Tester #2', musicbrainz_id=u'2')
        license = License(id=u'Test', full_name=u'Test License')
        db.session.add(license)
        db.session.commit()
        review = Review.create(release_group='e7aad618-fa86-3983-9e77-405e21796eca',
                               text=u"Testing!",
                               user=author,
                               is_draft=False,
                               license_id=license.id)

        vote_u1_positive = Vote.create(user_1, review, True)

        votes = db.session.query(Vote).all()
        self.assertEqual(len(votes), 1)
        self.assertIn(vote_u1_positive, votes)

        vote_u2_negative = Vote.create(user_2, review, False)

        votes = db.session.query(Vote).all()
        self.assertEqual(len(votes), 2)
        self.assertIn(vote_u1_positive, votes)
        self.assertIn(vote_u2_negative, votes)

        # TODO: Test vote overwriting
