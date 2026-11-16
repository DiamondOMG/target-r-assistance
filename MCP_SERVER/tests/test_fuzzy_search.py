import unittest
from jarvis_mcp.fuzzy_search import calculate_similarity, targetr_fuzzy_search


class TestFuzzySearch(unittest.TestCase):
    def setUp(self):
        self.mock_locations = [
            {
                "store_location": "TopsDigital-Centralworld",
                "thai_name": "ท็อปส์ เซ็นทรัลเวิลด์",
                "aliases": "เซ็นทรัลเวิลด์, Central World, CTW, ราชประสงค์",
                "retailer": "Tops",
                "store_code": "022, TM022",
                "notes": ""
            },
            {
                "store_location": "TopsDigital-Ladprao",
                "thai_name": "ท็อปส์ ลาดพร้าว",
                "aliases": "ลาดพร้าว, เซ็นทรัลลาดพร้าว",
                "retailer": "Tops",
                "store_code": "010, TM010",
                "notes": ""
            },
            {
                "store_location": "Bangphlee",
                "thai_name": "บิ๊กซี บางพลี",
                "aliases": "บางพลี, บิ๊กซีบางพลี",
                "retailer": "Big C",
                "store_code": "11106, BC11106",
                "notes": ""
            }
        ]

    def test_calculate_similarity(self):
        # Exact match
        self.assertEqual(calculate_similarity("CTW", "CTW"), 1.0)
        # Substring
        self.assertGreaterEqual(calculate_similarity("ลาดพร้าว", "ท็อปส์ ลาดพร้าว"), 0.85)
        # Misspelled Thai
        self.assertGreater(calculate_similarity("เซลทรัลเวิล", "เซ็นทรัลเวิลด์"), 0.75)
        # Misspelled English
        self.assertGreater(calculate_similarity("Centrl Wold", "Central World"), 0.85)

    def test_fuzzy_search_thai_misspelling(self):
        # User searches with typo: "เซลทรัลเวิล"
        res = targetr_fuzzy_search(
            query="เซลทรัลเวิล",
            entity_type="location",
            threshold=0.6,
            records_override=self.mock_locations
        )
        self.assertGreaterEqual(res["total_matched"], 1)
        top = res["results"][0]
        self.assertEqual(top["store_location"], "TopsDigital-Centralworld")
        self.assertGreater(top["score"], 0.75)

    def test_fuzzy_search_alias_code(self):
        # User searches with abbreviation "CTW"
        res = targetr_fuzzy_search(
            query="CTW",
            entity_type="location",
            threshold=0.8,
            records_override=self.mock_locations
        )
        self.assertEqual(res["results"][0]["store_location"], "TopsDigital-Centralworld")
        self.assertEqual(res["results"][0]["score"], 1.0)

        # User searches with STC code "TM022"
        res_code = targetr_fuzzy_search(
            query="TM022",
            entity_type="location",
            threshold=0.8,
            records_override=self.mock_locations
        )
        self.assertEqual(res_code["results"][0]["store_location"], "TopsDigital-Centralworld")

    def test_fuzzy_search_english_misspelling(self):
        # Typo: "Bangplee" (missing 'h')
        res = targetr_fuzzy_search(
            query="Bangplee",
            entity_type="location",
            threshold=0.7,
            records_override=self.mock_locations
        )
        self.assertGreaterEqual(res["total_matched"], 1)
        self.assertEqual(res["results"][0]["store_location"], "Bangphlee")


if __name__ == "__main__":
    unittest.main()

