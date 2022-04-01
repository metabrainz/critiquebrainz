from unittest import mock
import uuid

import critiquebrainz.db.review as db_review
import critiquebrainz.db.license as db_license
from critiquebrainz.db.user import User
import critiquebrainz.db.users as db_users
from critiquebrainz.ws.exceptions import InvalidRequest
from critiquebrainz.ws.review.bulk import _validate_bulk_params
from critiquebrainz.ws.testing import WebServiceTestCase


class BulkReviewTestCase(WebServiceTestCase):

    def test_validate_params(self):
        # Valid UUIDs
        review_ids = "001b8830-4b49-4fff-9ec5-2e1d88941146,001111e3-a474-4cec-85bf-7e95f2cbf145"
        parsed_review_ids, review_id_mapping = _validate_bulk_params(review_ids)
        self.assertEqual(parsed_review_ids, ["001b8830-4b49-4fff-9ec5-2e1d88941146", "001111e3-a474-4cec-85bf-7e95f2cbf145"])
        self.assertEqual(review_id_mapping, 
            {"001b8830-4b49-4fff-9ec5-2e1d88941146": "001b8830-4b49-4fff-9ec5-2e1d88941146",
             "001111e3-a474-4cec-85bf-7e95f2cbf145": "001111e3-a474-4cec-85bf-7e95f2cbf145"}
        )

        # Extra comma
        review_ids = "001b8830-4b49-4fff-9ec5-2e1d88941146,,001111e3-a474-4cec-85bf-7e95f2cbf145"
        parsed_review_ids, review_id_mapping = _validate_bulk_params(review_ids)
        self.assertEqual(parsed_review_ids, ["001b8830-4b49-4fff-9ec5-2e1d88941146", "001111e3-a474-4cec-85bf-7e95f2cbf145"])

        # Valid, but not formatted as expected
        review_ids = "001B8830-4B49-4FFF-9EC5-2E1D88941146,001111e3a4744cec85bf7e95f2cbf145"
        parsed_review_ids, review_id_mapping = _validate_bulk_params(review_ids)
        self.assertEqual(parsed_review_ids, ["001b8830-4b49-4fff-9ec5-2e1d88941146", "001111e3-a474-4cec-85bf-7e95f2cbf145"])
        self.assertEqual(review_id_mapping, 
            {"001B8830-4B49-4FFF-9EC5-2E1D88941146": "001b8830-4b49-4fff-9ec5-2e1d88941146",
             "001111e3a4744cec85bf7e95f2cbf145": "001111e3-a474-4cec-85bf-7e95f2cbf145"}
        )

        # Duplicated
        review_ids = "001b8830-4b49-4fff-9ec5-2e1d88941146,001111e3-a474-4cec-85bf-7e95f2cbf145,001b8830-4b49-4fff-9ec5-2e1d88941146"
        parsed_review_ids, review_id_mapping = _validate_bulk_params(review_ids)
        self.assertEqual(parsed_review_ids, ["001b8830-4b49-4fff-9ec5-2e1d88941146", "001111e3-a474-4cec-85bf-7e95f2cbf145"])

        # Invalid UUID
        review_ids = "001111e3-a474-4cec-85bf-7e95f2cbf145,this-isnt-valid,"
        with self.assertRaises(InvalidRequest):
            _validate_bulk_params(review_ids)

    def test_validate_params_request(self):
        # Missing query parameter
        response = self.client.get('/reviews/')
        self.assert200(response)
        self.assertEqual(response.json, {"review_id_mapping": {}, "reviews": {}})

        response = self.client.get('/reviews/', query_string={'review_ids': ''})
        self.assert200(response)
        self.assertEqual(response.json, {"review_id_mapping": {}, "reviews": {}})

        uuids = [str(uuid.uuid4()) for _ in range(26)]
        # Too many items
        response = self.client.get('/reviews/', query_string={'review_ids': ','.join(uuids)})
        self.assert400(response)
        self.assertEqual(response.json['description'], "More than 25 recordings not allowed per request")

    @mock.patch('critiquebrainz.db.review.get_by_ids')
    def test_bulk_reviews_mock(self, mock_db_review):
        # pass query parameters through to the bulk get method
        mock_db_review.return_value = []
        uuids = ["001b8830-4b49-4fff-9ec5-2e1d88941146", "001111e3-a474-4cec-85bf-7e95f2cbf145"]
        self.client.get('/reviews/', query_string={'review_ids': ','.join(uuids)})
        mock_db_review.assert_called_with(uuids)

    def test_bulk_reviews_return_values(self):
        # If a review is hidden it shouldn't be returned even if the id is correct
        # review_id_mapping shouldn't include review_ids uuids which aren't returned from the DB
        self.user = User(db_users.get_or_create(1, "Tester", new_user_data={
            "display_name": "test user",
        }))
        self.license = db_license.create(
            id=u'Test',
            full_name=u"Test License",
        )
        review1 = db_review.create(
            user_id=self.user.id,
            entity_id="e7aad618-fa86-3983-9e77-405e21796eca",
            entity_type="release_group",
            text="Testing",
            rating=5,
            is_draft=False,
            license_id=self.license["id"],
        )
        r1_id = str(review1["id"])
        review2 = db_review.create(
            user_id=self.user.id,
            entity_id="3cfb11bb-135f-4841-a800-c056eb7465e0",
            entity_type="release_group",
            text="Another test",
            is_draft=False,
            license_id=self.license["id"],
        )
        r2_id = str(review2["id"])
        db_review.set_hidden_state(review2["id"], is_hidden=True)

        uuids = [r1_id, r2_id, "c7fef1f9-4dcb-4dd4-a7f7-7e68279bcc28"]
        response = self.client.get('/reviews/', query_string={'review_ids': ','.join(uuids)})
        self.assertEqual(list(response.json['reviews'].keys()), [r1_id])
        self.assertEqual(list(response.json['review_id_mapping'].keys()), [r1_id])
