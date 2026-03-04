import unittest
from app import create_app


class TestReviewEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.testing = True

        # owner
        r_owner = self.client.post("/api/v1/users/", json={
            "first_name": "Alice", "last_name": "Smith",
            "email": "alice@example.com", "password": "Password123"
        })
        self.owner_id = r_owner.get_json()["id"]

        # normal user
        r_user = self.client.post("/api/v1/users/", json={
            "first_name": "Bob", "last_name": "Jones",
            "email": "bob@example.com", "password": "Password123"
        })
        self.user_id = r_user.get_json()["id"]

        # place
        r_place = self.client.post("/api/v1/places/", json={
            "title": "Cozy Apartment",
            "description": "Nice",
            "price": 100.0,
            "latitude": 37.7749,
            "longitude": -122.4194,
            "owner_id": self.owner_id,
            "amenities": []
        })
        self.place_id = r_place.get_json()["id"]

        self.valid_review = {
            "text": "Great place!",
            "rating": 5,
            "user_id": self.user_id,
            "place_id": self.place_id
        }

    def _create_review(self, payload=None):
        return self.client.post("/api/v1/reviews/", json=payload or self.valid_review)

    def test_create_review_success(self):
        r = self._create_review()
        self.assertEqual(r.status_code, 201)
        data = r.get_json()
        self.assertIn("id", data)
        self.assertEqual(data["text"], "Great place!")
        self.assertEqual(data["rating"], 5)

    def test_create_review_invalid_rating(self):
        r = self._create_review({**self.valid_review, "rating": 6})
        self.assertEqual(r.status_code, 400)

    def test_create_review_empty_text(self):
        r = self._create_review({**self.valid_review, "text": ""})
        self.assertEqual(r.status_code, 400)

    def test_create_review_invalid_user(self):
        r = self._create_review({**self.valid_review, "user_id": "fake-id"})
        self.assertEqual(r.status_code, 400)

    def test_create_review_invalid_place(self):
        r = self._create_review({**self.valid_review, "place_id": "fake-id"})
        self.assertEqual(r.status_code, 400)

    def test_owner_cannot_review_own_place(self):
        r = self._create_review({**self.valid_review, "user_id": self.owner_id})
        self.assertEqual(r.status_code, 400)

    def test_get_all_reviews_empty(self):
        r = self.client.get("/api/v1/reviews/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json(), [])

    def test_get_all_reviews(self):
        self._create_review()
        r = self.client.get("/api/v1/reviews/")
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.get_json(), list)
        self.assertGreaterEqual(len(r.get_json()), 1)

    def test_get_review_by_id(self):
        post = self._create_review()
        review_id = post.get_json()["id"]

        r = self.client.get(f"/api/v1/reviews/{review_id}")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIn("text", data)
        self.assertIn("user_id", data)
        self.assertIn("place_id", data)

    def test_get_review_not_found(self):
        r = self.client.get("/api/v1/reviews/fake-id-000")
        self.assertEqual(r.status_code, 404)

    def test_update_review_success(self):
        post = self._create_review()
        review_id = post.get_json()["id"]

        r = self.client.put(
            f"/api/v1/reviews/{review_id}",
            json={**self.valid_review, "text": "Amazing!", "rating": 4}
        )
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertTrue(("message" in data) or ("id" in data) or ("text" in data))

    def test_update_review_not_found(self):
        r = self.client.put(
            "/api/v1/reviews/fake-id-000",
            json=self.valid_review
        )
        self.assertEqual(r.status_code, 404)

    def test_delete_review_success(self):
        post = self._create_review()
        review_id = post.get_json()["id"]

        r = self.client.delete(f"/api/v1/reviews/{review_id}")
        self.assertEqual(r.status_code, 200)
        self.assertIn("message", r.get_json())

    def test_delete_review_not_found(self):
        r = self.client.delete("/api/v1/reviews/fake-id-000")
        self.assertEqual(r.status_code, 404)

    def test_get_reviews_by_place(self):
        self._create_review()
        r = self.client.get(f"/api/v1/places/{self.place_id}/reviews")
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.get_json(), list)

    def test_get_reviews_by_place_not_found(self):
        r = self.client.get("/api/v1/places/fake-id/reviews")
        self.assertEqual(r.status_code, 404)


if __name__ == "__main__":
    unittest.main()
