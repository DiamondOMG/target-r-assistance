import unittest
from jarvis_mcp.geo_distance import calculate_haversine_distance, geo_distance


class TestGeoDistance(unittest.TestCase):
    def setUp(self):
        # Central World approx coords
        self.central_world = {"latitude": 13.7469, "longitude": 100.5398}

        # Mock destinations (ห้างรอบ Central World)
        self.mock_destinations = [
            {
                "id": "screen_gaysorn",
                "label": "Gaysorn Village",
                "latitude": 13.7447,
                "longitude": 100.5412,
            },
            {
                "id": "screen_paragon",
                "label": "Siam Paragon",
                "latitude": 13.7460,
                "longitude": 100.5350,
            },
            {
                "id": "screen_mega_bangna",
                "label": "Mega Bangna",
                "latitude": 13.6457,
                "longitude": 100.6802,
            },
            {
                "id": "screen_invalid_coords",
                "label": "Invalid Mall",
                "latitude": None,
                "longitude": None,
            },
        ]

    def test_haversine_same_point(self):
        dist = calculate_haversine_distance(13.7469, 100.5398, 13.7469, 100.5398)
        self.assertEqual(dist, 0.0)

    def test_geo_distance_sorting_and_filtering(self):
        # Test finding nearby within 3 km
        res = geo_distance(
            origin=self.central_world,
            destinations=self.mock_destinations,
            max_distance_km=3.0,
            limit=5,
            unit="km",
        )

        self.assertEqual(res["source"], "geo_calc")
        self.assertEqual(res["total_matched"], 2)  # Gaysorn and Paragon, excluding Mega Bangna (>15km) and invalid
        self.assertEqual(res["returned"], 2)

        # Sorted by distance: Gaysorn should be closer than Paragon
        self.assertEqual(res["results"][0]["id"], "screen_gaysorn")
        self.assertEqual(res["results"][1]["id"], "screen_paragon")
        self.assertLess(res["results"][0]["distance"], res["results"][1]["distance"])

    def test_geo_distance_limit(self):
        res = geo_distance(
            origin=self.central_world,
            destinations=self.mock_destinations,
            limit=1,
            unit="km",
        )
        self.assertEqual(res["returned"], 1)
        self.assertEqual(res["results"][0]["id"], "screen_gaysorn")

    def test_geo_distance_unit_meters(self):
        res = geo_distance(
            origin=self.central_world,
            destinations=[self.mock_destinations[0]],
            unit="m",
        )
        self.assertEqual(res["results"][0]["unit"], "m")
        self.assertGreater(res["results"][0]["distance"], 100.0)

    def test_invalid_origin_raises(self):
        with self.assertRaises(ValueError):
            geo_distance(origin={}, destinations=[])

        with self.assertRaises(ValueError):
            geo_distance(origin={"latitude": 120.0, "longitude": 100.0}, destinations=[])


if __name__ == "__main__":
    unittest.main()

