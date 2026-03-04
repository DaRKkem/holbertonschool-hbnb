import unittest
from app import create_app


class TestUserEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.testing = True

    def _create_user(self, email="john.doe@example.com"):
        payload = {
            "first_name": "John",
            "last_name": "Doe",
            "email": email,
            "password": "Password123"
        }
        return self.client.post("/api/v1/users/", json=payload)

    def test_create_user_success(self):
        r = self._create_user()
        self.assertEqual(r.status_code, 201)
        data = r.get_json()
        self.assertIn("id", data)
        self.assertEqual(data["email"], "john.doe@example.com")
        self.assertNotIn("password", data)

    def test_create_user_duplicate_email(self):
        self._create_user()
        r = self._create_user()
        self.assertEqual(r.status_code, 400)

    def test_create_user_invalid_email(self):
        payload = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "not-an-email",
            "password": "Password123"
        }
        r = self.client.post("/api/v1/users/", json=payload)
        self.assertEqual(r.status_code, 400)

    def test_create_user_missing_field(self):
        r = self.client.post("/api/v1/users/", json={"first_name": "John"})
        self.assertEqual(r.status_code, 400)

    def test_create_user_empty_first_name(self):
        payload = {
            "first_name": "",
            "last_name": "Doe",
            "email": "a@b.com",
            "password": "Password123"
        }
        r = self.client.post("/api/v1/users/", json=payload)
        self.assertEqual(r.status_code, 400)

    def test_get_all_users_empty(self):
        r = self.client.get("/api/v1/users/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json(), [])

    def test_get_all_users(self):
        self._create_user()
        r = self.client.get("/api/v1/users/")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)

    def test_get_user_by_id_success(self):
        post = self._create_user()
        user_id = post.get_json()["id"]

        r = self.client.get(f"/api/v1/users/{user_id}")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data["id"], user_id)
        self.assertNotIn("password", data)

    def test_get_user_not_found(self):
        r = self.client.get("/api/v1/users/fake-id-000")
        self.assertEqual(r.status_code, 404)

    def test_update_user_success_partial(self):
        post = self._create_user()
        user_id = post.get_json()["id"]

        r = self.client.put(f"/api/v1/users/{user_id}", json={"first_name": "Jane"})
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data["first_name"], "Jane")
        self.assertNotIn("password", data)

    def test_update_user_not_found(self):
        r = self.client.put("/api/v1/users/fake-id-000", json={"first_name": "Jane"})
        self.assertEqual(r.status_code, 404)

    def test_update_user_duplicate_email(self):
        u1 = self._create_user("john.doe@example.com").get_json()["id"]
        u2 = self._create_user("other@example.com").get_json()["id"]

        r = self.client.put(f"/api/v1/users/{u2}", json={"email": "john.doe@example.com"})
        self.assertEqual(r.status_code, 400)


if __name__ == "__main__":
    unittest.main()
