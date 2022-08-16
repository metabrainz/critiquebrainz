from critiquebrainz.frontend.external.bookbrainz_db import series
from critiquebrainz.data.testing import DataTestCase


class SeriesTestCase(DataTestCase):
    def setUp(self):
        super(SeriesTestCase, self).setUp()
        self.bbid1 = "e6f48cbd-26de-4c2e-a24a-29892f9eb3be"
        self.bbid2 = "29b7d60f-0be1-428d-8a2d-71f3abb8d218"
        self.bbid3 = "968ef651-6a70-410f-9b17-f326ee0062c3"

    def test_get_series_by_bbid(self):
        series_info = series.get_series_by_bbid(self.bbid1)
        self.assertEqual(series_info["bbid"], self.bbid1)
        self.assertEqual(series_info["name"], "Harry Potter")
        self.assertEqual(series_info["sort_name"], "Harry Potter")
        self.assertEqual(series_info["series_type"], "Work")

    def test_fetch_multiple_series(self):
        series_info = series.fetch_multiple_series([self.bbid2, self.bbid3])
        self.assertEqual(len(series_info), 2)
        self.assertEqual(series_info[self.bbid2]["bbid"], self.bbid2)
        self.assertEqual(series_info[self.bbid2]["name"], "The Lord of the Rings")
        self.assertEqual(series_info[self.bbid2]["series_type"], "Work")
        self.assertEqual(series_info[self.bbid3]["bbid"], self.bbid3)
        self.assertEqual(series_info[self.bbid3]["name"], "The Hunger Games")
        self.assertEqual(series_info[self.bbid3]["series_type"], "Work")
