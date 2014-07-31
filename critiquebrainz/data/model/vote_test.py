from critiquebrainz.testing import ServerTestCase
from critiquebrainz.data import db
from vote import Vote
from user import User
from review import Review
from license import License


class VoteTestCase(ServerTestCase):

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
                               license_id=license.id)

        vote_u1_positive = Vote.create(user_1, review, True)

        votes = db.session.query(Vote).all()
        assert len(votes) == 1 and vote_u1_positive in votes

        vote_u2_negative = Vote.create(user_2, review, False)

        votes = db.session.query(Vote).all()
        assert len(votes) == 2 and vote_u1_positive in votes and vote_u2_negative in votes

        # TODO: Test vote overwriting
