import unittest
from app import create_app


class TestAmenityEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.testing = True

    def _create_amenity(self, name="Wi-Fi"):
        # on envoie aussi description (si l’API l’accepte)
        payload = {"name": name, "description": "Fast internet"}
        return self.client.post("/api/v1/amenities/", json=payload)

    def test_create_amenity_success(self):
        r = self._create_amenity()
        self.assertEqual(r.status_code, 201)
        data = r.get_json()
        self.assertIn("id", data)
        self.assertEqual(data["name"], "Wi-Fi")

    def test_create_amenity_empty_name(self):
        r = self._create_amenity("")
        self.assertEqual(r.status_code, 400)

    def test_create_amenity_name_too_long(self):
        r = self._create_amenity("A" * 51)
        self.assertEqual(r.status_code, 400)

    def test_get_all_amenities_empty(self):
        r = self.client.get("/api/v1/amenities/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json(), [])

    def test_get_all_amenities(self):
        self._create_amenity("Wi-Fi")
        r = self.client.get("/api/v1/amenities/")
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.get_json(), list)
        self.assertGreaterEqual(len(r.get_json()), 1)

    def test_get_amenity_by_id(self):
        post = self._create_amenity("Wi-Fi")
        amenity_id = post.get_json()["id"]

        r = self.client.get(f"/api/v1/amenities/{amenity_id}")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["id"], amenity_id)

    def test_get_amenity_not_found(self):
        r = self.client.get("/api/v1/amenities/fake-id-000")
        self.assertEqual(r.status_code, 404)

    def test_update_amenity_success(self):
        post = self._create_amenity("Wi-Fi")
        amenity_id = post.get_json()["id"]

        r = self.client.put(
            f"/api/v1/amenities/{amenity_id}",
            json={"name": "Air Conditioning", "description": "Cool air"}
        )
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        # selon votre API : soit "message", soit l’objet
        self.assertTrue(("message" in data) or ("id" in data))

    def test_update_amenity_not_found(self):
        r = self.client.put("/api/v1/amenities/fake-id-000", json={"name": "Air Conditioning"})
        self.assertEqual(r.status_code, 404)


if __name__ == "__main__":
    unittest.main()
