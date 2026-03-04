import unittest
from app import create_app


class TestPlaceEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.testing = True

        # create owner
        r = self.client.post("/api/v1/users/", json={
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice@example.com",
            "password": "Password123"
        })
        self.owner_id = r.get_json()["id"]

        self.valid_place = {
            "title": "Cozy Apartment",
            "description": "A nice place",
            "price": 100.0,
            "latitude": 37.7749,
            "longitude": -122.4194,
            "owner_id": self.owner_id,
            "amenities": []
        }

    def _create_place(self, payload=None):
        return self.client.post("/api/v1/places/", json=payload or self.valid_place)

    def test_create_place_success(self):
        r = self._create_place()
        self.assertEqual(r.status_code, 201)
        data = r.get_json()
        self.assertIn("id", data)
        self.assertEqual(data["title"], "Cozy Apartment")

    def test_create_place_invalid_owner(self):
        payload = {**self.valid_place, "owner_id": "fake-id"}
        r = self._create_place(payload)
        self.assertEqual(r.status_code, 400)

    def test_create_place_negative_price(self):
        payload = {**self.valid_place, "price": -10.0}
        r = self._create_place(payload)
        self.assertEqual(r.status_code, 400)

    def test_create_place_invalid_latitude(self):
        payload = {**self.valid_place, "latitude": 95.0}
        r = self._create_place(payload)
        self.assertEqual(r.status_code, 400)

    def test_create_place_invalid_longitude(self):
        payload = {**self.valid_place, "longitude": 200.0}
        r = self._create_place(payload)
        self.assertEqual(r.status_code, 400)

    def test_create_place_empty_title(self):
        payload = {**self.valid_place, "title": ""}
        r = self._create_place(payload)
        self.assertEqual(r.status_code, 400)

    def test_get_all_places_empty(self):
        r = self.client.get("/api/v1/places/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json(), [])

    def test_get_all_places(self):
        self._create_place()
        r = self.client.get("/api/v1/places/")
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.get_json(), list)
        self.assertGreaterEqual(len(r.get_json()), 1)

    def test_get_place_by_id(self):
        post = self._create_place()
        place_id = post.get_json()["id"]

        r = self.client.get(f"/api/v1/places/{place_id}")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data["id"], place_id)
        # owner / amenities peuvent être sérialisés ou non selon votre API
        self.assertIn("title", data)

    def test_get_place_not_found(self):
        r = self.client.get("/api/v1/places/fake-id-000")
        self.assertEqual(r.status_code, 404)

    def test_update_place_success(self):
        post = self._create_place()
        place_id = post.get_json()["id"]

        r = self.client.put(
            f"/api/v1/places/{place_id}",
            json={"title": "Luxury Condo", "price": 200.0}
        )
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertTrue(("message" in data) or ("id" in data) or ("title" in data))

    def test_update_place_not_found(self):
        r = self.client.put("/api/v1/places/fake-id-000", json={"title": "X"})
        self.assertEqual(r.status_code, 404)


if __name__ == "__main__":
    unittest.main()
