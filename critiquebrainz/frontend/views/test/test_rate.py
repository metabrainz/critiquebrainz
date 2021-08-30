# critiquebrainz - Repository for Creative Commons licensed reviews
#
# Copyright (C) 2018 Bimalkant Lauhny.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from flask import url_for

import critiquebrainz.db.license as db_license
import critiquebrainz.db.review as db_review
import critiquebrainz.db.users as db_users
from critiquebrainz.db.user import User
from critiquebrainz.frontend.testing import FrontendTestCase


class RateViewsTestCase(FrontendTestCase):

    def setUp(self):
        super(RateViewsTestCase, self).setUp()
        self.reviewer = User(db_users.get_or_create(1, "aef06569-098f-4218-a577-b413944d9493", new_user_data={
            "display_name": u"Reviewer",
        }))
        self.license = db_license.create(
            id="CC BY-SA 3.0",
            full_name="Test License.",
        )

    def test_rate(self):
        self.temporary_login(self.reviewer)
        entity_id = 'e7aad618-fa86-3983-9e77-405e21796eca'
        # Test for first time rating (no review exists)
        payload = {
            'entity_id': entity_id,
            'entity_type': 'release_group',
            'rating': 4
        }
        response = self.client.post(
            url_for('rate.rate'),
            data=payload
        )

        self.assertRedirects(response, '/release-group/{}'.format(entity_id))

        reviews, review_count = db_review.list_reviews(
            entity_id=entity_id,
            entity_type='release_group',
            user_id=self.reviewer.id
        )
        # Test that the rate request created a review
        self.assertEqual(review_count, 1)
        review = reviews[0]
        self.assertEqual(review['text'], None)
        self.assertEqual(review['rating'], 4)

        response = self.client.get('/release-group/{}'.format(entity_id))
        self.assert200(response)
        self.assertIn('We have updated your rating for this entity!', str(response.data))

        # Test after rating is cleared for review with NO text
        payload = {
            'entity_id': entity_id,
            'entity_type': 'release_group',
            'rating': None
        }
        response = self.client.post(
            url_for('rate.rate'),
            data=payload
        )

        reviews, review_count = db_review.list_reviews(
            entity_id=entity_id,
            entity_type='release_group',
            user_id=self.reviewer.id
        )
        # Test that the clear rating request results in deletion of review (because review-text was None)
        self.assertEqual(review_count, 0)

        # Test after rating is cleared for review with some text
        self.review = db_review.create(
            user_id=self.reviewer.id,
            entity_id=entity_id,
            entity_type="release_group",
            text="Test Review.",
            rating=4,
            is_draft=False,
            license_id=self.license["id"],
        )

        payload = {
            'entity_id': entity_id,
            'entity_type': 'release_group',
            'rating': None
        }
        response = self.client.post(
            url_for('rate.rate'),
            data=payload
        )

        reviews, review_count = db_review.list_reviews(
            entity_id=entity_id,
            entity_type='release_group',
            user_id=self.reviewer.id
        )
        # Test that the clear rating request doesn't delete review (because review-text was not None)
        self.assertEqual(review_count, 1)
        review = reviews[0]
        self.assertEqual(review['rating'], None)

    def test_artist_rating(self):
        self.temporary_login(self.reviewer)
        test_entity_id = 'f59c5520-5f46-4d2c-b2c4-822eabf53419'
        payload = {
            'entity_id': test_entity_id,
            'entity_type': 'artist',
            'rating': 4
        }

        response = self.client.post(url_for('rate.rate'), data=payload)
        self.assertRedirects(response, '/artist/{}'.format(test_entity_id))
        reviews, review_count = db_review.list_reviews(
            entity_id=test_entity_id,
            entity_type='artist',
            user_id=self.reviewer.id
        )

        self.assertEqual(review_count, 1)
        self.assertEqual(reviews[0]['rating'], 4)

        response = self.client.get('/artist/{}'.format(test_entity_id))
        self.assert200(response)
        self.assertIn('We have updated your rating for this entity!', str(response.data))
