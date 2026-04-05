"""
tests_lite.py — Tests unitaires HBnB Part 3
Chaque test est complètement indépendant (DB en RAM, remise à zéro à chaque test).
Pas besoin de lancer le serveur Flask.

Lancer avec :
    python3 -m unittest tests/tests_lite.py -v
    pytest tests/tests_lite.py -v
    pytest tests/tests_lite.py::TestAuth -v
    pytest tests/tests_lite.py::TestReviews::test_doublon_interdit -v
"""

import unittest
from app import create_app, db
from app.models.user import User


class TestBase(unittest.TestCase):
    """
    Classe de base : DB SQLite en RAM, admin seedé, remise à zéro après chaque test.
    Chaque test a sa propre DB vierge — aucune dépendance entre les tests.
    """

    def setUp(self):
        self.app = create_app("config.TestingConfig")
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            # Insérer l'admin directement en DB (l'API bloque is_admin)
            admin = User(
                first_name="Admin",
                last_name="HBnB",
                email="admin@hbnb.io",
                is_admin=True
            )
            admin.hash_password("admin1234")
            db.session.add(admin)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # -------------------------------------------------------
    # Helpers — réutilisés dans tous les tests
    # -------------------------------------------------------

    def _login(self, email, password):
        """POST /auth/login → retourne le token JWT ou None."""
        r = self.client.post('/api/v1/auth/login',
                            json={"email": email, "password": password})
        return r.get_json().get("access_token")

    def _auth(self, token):
        """Retourne le header Authorization pour un token donné."""
        return {"Authorization": f"Bearer {token}"}

    def _create_user(self, email, password="pass1234",
                    first_name="Test", last_name="User"):
        """Crée un user via l'API et retourne (user_id, token)."""
        # login en admin
        admin_token = self._login("admin@hbnb.io", "admin1234")

        # creation avec header authorization
        r = self.client.post('/api/v1/users/', json={
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password
        },headers=self._auth(admin_token))

        self.assertEqual(r.status_code, 201,
                        f"Échec création user {email}: {r.get_json()}")
        user_id = r.get_json()["id"]
        token = self._login(email, password)
        return user_id, token

    def _create_amenity(self, name="WiFi", description="Test amenity"):
        """Crée une amenity en tant qu'admin et retourne son id."""
        token = self._login("admin@hbnb.io", "admin1234")
        r = self.client.post('/api/v1/amenities/',
                            json={"name": name, "description": description},
                            headers=self._auth(token))
        self.assertEqual(r.status_code, 201,
                        f"Échec création amenity '{name}': {r.get_json()}")
        return r.get_json()["id"]

    def _create_place(self, token, title="Studio Test", price=50,
                    amenities=None):
        """Crée une place et retourne son id."""
        r = self.client.post('/api/v1/places/', json={
            "title": title,
            "description": "Nice place for testing",
            "price": price,
            "latitude": 45.0,
            "longitude": 6.0,
            "amenities": amenities or []
        }, headers=self._auth(token))
        self.assertEqual(r.status_code, 201,
                        f"Échec création place '{title}': {r.get_json()}")
        return r.get_json()["id"]

    def _create_review(self, token, place_id,
                    text="Super endroit !", rating=5):
        """Crée une review et retourne la réponse complète."""
        return self.client.post('/api/v1/reviews/', json={
            "text": text,
            "rating": rating,
            "place_id": place_id
        }, headers=self._auth(token))


# =============================================================================
# SECTION 1 — AUTH
# =============================================================================

class TestAuth(TestBase):
    """Tests du login JWT."""

    def setUp(self):
        super().setUp()
        # Créer John une seule fois pour cette classe
        self.john_id, self.john_token = self._create_user("john@test.com")

    def test_login_valide_retourne_token(self):
        """Login avec bons identifiants → 200 + access_token."""
        r = self.client.post('/api/v1/auth/login',
                            json={"email": "john@test.com",
                                "password": "pass1234"})
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIn("access_token", data)
        self.assertIsInstance(data["access_token"], str)
        self.assertGreater(len(data["access_token"]), 0)

    def test_login_mauvais_mot_de_passe(self):
        """Login avec mauvais mot de passe → 401."""
        r = self.client.post('/api/v1/auth/login',
                            json={"email": "john@test.com",
                                "password": "mauvais"})
        self.assertEqual(r.status_code, 401)

    def test_login_email_inexistant(self):
        """Login avec email inconnu → 401."""
        r = self.client.post('/api/v1/auth/login',
                            json={"email": "ghost@test.com",
                                "password": "pass1234"})
        self.assertEqual(r.status_code, 401)

    def test_endpoint_protege_sans_token(self):
        """Accès endpoint protégé sans token → 401."""
        r = self.client.post('/api/v1/amenities/', json={"name": "Test"})
        self.assertEqual(r.status_code, 401)

    def test_endpoint_protege_avec_token_admin(self):
        """Accès endpoint admin avec token admin → 201."""
        token = self._login("admin@hbnb.io", "admin1234")
        r = self.client.post('/api/v1/amenities/',
                            json={"name": "TestToken"},
                            headers=self._auth(token))
        self.assertEqual(r.status_code, 201)


# =============================================================================
# SECTION 2 — USERS
# =============================================================================

class TestUsersCreate(TestBase):
    """Tests de création d'utilisateurs."""

    def test_creer_user_valide(self):
        """Créer un user valide → 201 sans password dans la réponse."""

        admin_token = self._login("admin@hbnb.io", "admin1234")

        r = self.client.post('/api/v1/users/', json={
            "first_name": "Sara", "last_name": "Rebati",
            "email": "sara@test.com", "password": "pass1234"
        }, headers=self._auth(admin_token))

        self.assertEqual(r.status_code, 201)
        data = r.get_json()
        self.assertIn("id", data)
        self.assertIn("email", data)
        self.assertNotIn("password", data)  # ← mot de passe jamais retourné

    def test_email_duplique_rejete(self):
        """Même email deux fois → 422."""

        admin_token = self._login("admin@hbnb.io", "admin1234")

        self._create_user("dup@test.com")
        r = self.client.post('/api/v1/users/', json={
            "first_name": "X", "last_name": "Y",
            "email": "dup@test.com", "password": "pass1234"
        }, headers=self._auth(admin_token))

        self.assertEqual(r.status_code, 422)


class TestUsersRead(TestBase):
    """Tests de lecture d'utilisateurs."""

    def setUp(self):
        super().setUp()
        self.john_id, self.john_token = self._create_user("john@test.com")

    def test_get_user_par_id(self):
        """GET /users/<id> retourne le bon user sans password."""
        r = self.client.get(f'/api/v1/users/{self.john_id}')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data["id"], self.john_id)
        self.assertNotIn("password", data)

    def test_get_user_inexistant(self):
        """GET user avec ID inconnu → 404."""
        r = self.client.get(
            '/api/v1/users/00000000-0000-0000-0000-000000000000')
        self.assertEqual(r.status_code, 404)

    def test_lister_tous_les_users(self):
        """GET /users/ retourne au moins admin + John."""
        r = self.client.get('/api/v1/users/')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 2)


class TestUsersUpdate(TestBase):
    """Tests de modification d'utilisateurs."""

    def setUp(self):
        super().setUp()
        self.admin_token = self._login("admin@hbnb.io", "admin1234")
        self.john_id, self.john_token = self._create_user("john@test.com")
        self.jane_id, self.jane_token = self._create_user("jane@test.com")

    def test_modifier_son_propre_prenom(self):
        """User peut modifier son propre first_name → 200."""
        r = self.client.put(f'/api/v1/users/{self.john_id}',
                            json={"first_name": "Johnny"},
                            headers=self._auth(self.john_token))
        self.assertEqual(r.status_code, 200)

    def test_modifier_profil_autre_interdit(self):
        """User ne peut pas modifier le profil d'un autre → 403."""
        r = self.client.put(f'/api/v1/users/{self.jane_id}',
                            json={"first_name": "Hacked"},
                            headers=self._auth(self.john_token))
        self.assertEqual(r.status_code, 403)

    def test_modifier_email_via_put_interdit(self):
        """PUT /users/<id> ne doit pas accepter de champ email → 400."""
        r = self.client.put(f'/api/v1/users/{self.john_id}',
                            json={"email": "new@test.com"},
                            headers=self._auth(self.john_token))
        self.assertEqual(r.status_code, 400)

    def test_modifier_sans_token_interdit(self):
        """PUT sans token → 401."""
        r = self.client.put(f'/api/v1/users/{self.john_id}',
                            json={"first_name": "NoToken"})
        self.assertEqual(r.status_code, 401)

    def test_admin_peut_modifier_nimporte_quel_user(self):
        """Admin peut modifier le profil de n'importe quel user → 200."""
        r = self.client.put(f'/api/v1/users/{self.john_id}',
                            json={"first_name": "AdminEdit"},
                            headers=self._auth(self.admin_token))
        self.assertEqual(r.status_code, 200)


# =============================================================================
# SECTION 3 — AMENITIES
# =============================================================================

class TestAmenitiesCreate(TestBase):
    """Tests de création d'amenities."""

    def setUp(self):
        super().setUp()
        self.admin_token = self._login("admin@hbnb.io", "admin1234")
        _, self.user_token = self._create_user("user@test.com")

    def test_admin_cree_amenity(self):
        """Admin crée une amenity avec description → 201."""
        r = self.client.post('/api/v1/amenities/',
                            json={"name": "Sauna", "description": "Sauna privé"},
                            headers=self._auth(self.admin_token))
        self.assertEqual(r.status_code, 201)
        data = r.get_json()
        self.assertIn("id", data)
        self.assertIn("description", data)

    def test_creer_sans_token(self):
        """Créer amenity sans token → 401."""
        r = self.client.post('/api/v1/amenities/', json={"name": "Test"})
        self.assertEqual(r.status_code, 401)

    def test_user_normal_cree_interdit(self):
        """User normal ne peut pas créer une amenity → 403."""
        r = self.client.post('/api/v1/amenities/',
                            json={"name": "Jacuzzi"},
                            headers=self._auth(self.user_token))
        self.assertEqual(r.status_code, 403)


class TestAmenitiesReadUpdate(TestBase):
    """Tests lecture et modification d'amenities."""

    def setUp(self):
        super().setUp()
        self.admin_token = self._login("admin@hbnb.io", "admin1234")
        _, self.user_token = self._create_user("user@test.com")
        self.amenity_id = self._create_amenity("Fireplace", "Cheminée privée")

    def test_get_amenity_par_id(self):
        """GET /amenities/<id> retourne la bonne amenity."""
        r = self.client.get(f'/api/v1/amenities/{self.amenity_id}')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data["id"], self.amenity_id)
        self.assertIn("description", data)

    def test_get_amenity_inexistante(self):
        """GET amenity inconnue → 404."""
        r = self.client.get(
            '/api/v1/amenities/00000000-0000-0000-0000-000000000000')
        self.assertEqual(r.status_code, 404)

    def test_lister_toutes_les_amenities(self):
        """GET /amenities/ retourne une liste."""
        r = self.client.get('/api/v1/amenities/')
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.get_json(), list)

    def test_admin_modifie_amenity(self):
        """Admin peut modifier une amenity → 200."""
        r = self.client.put(f'/api/v1/amenities/{self.amenity_id}',
                            json={"name": "Sauna VIP"},
                            headers=self._auth(self.admin_token))
        self.assertEqual(r.status_code, 200)

    def test_user_normal_modifie_interdit(self):
        """User normal ne peut pas modifier une amenity → 403."""
        r = self.client.put(f'/api/v1/amenities/{self.amenity_id}',
                            json={"name": "Hacked"},
                            headers=self._auth(self.user_token))
        self.assertEqual(r.status_code, 403)


# =============================================================================
# SECTION 4 — PLACES
# =============================================================================

class TestPlacesCreate(TestBase):
    """Tests de création de places."""

    def setUp(self):
        super().setUp()
        _, self.john_token = self._create_user("john@test.com")

    def test_creer_place_valide(self):
        """User connecté crée une place → 201 avec owner_id du JWT."""
        r = self.client.post('/api/v1/places/', json={
            "title": "Appartement Paris",
            "description": "Beau appart",
            "price": 120.0,
            "latitude": 48.85,
            "longitude": 2.35,
            "amenities": []
        }, headers=self._auth(self.john_token))
        self.assertEqual(r.status_code, 201)
        self.assertIn("id", r.get_json())

    def test_creer_sans_token(self):
        """Créer une place sans token → 401."""
        r = self.client.post('/api/v1/places/', json={
            "title": "X", "description": "Y",
            "price": 50, "latitude": 45.0, "longitude": 6.0, "amenities": []
        })
        self.assertEqual(r.status_code, 401)

    def test_prix_negatif_rejete(self):
        """Prix négatif → 400."""
        r = self.client.post('/api/v1/places/', json={
            "title": "Bad", "description": "Y",
            "price": -50, "latitude": 45.0, "longitude": 6.0, "amenities": []
        }, headers=self._auth(self.john_token))
        self.assertEqual(r.status_code, 400)

    def test_prix_zero_rejete(self):
        """Prix = 0 → 400 (le schema SQL dit price > 0)."""
        r = self.client.post('/api/v1/places/', json={
            "title": "Bad", "description": "Y",
            "price": 0, "latitude": 45.0, "longitude": 6.0, "amenities": []
        }, headers=self._auth(self.john_token))
        self.assertEqual(r.status_code, 400)

    def test_latitude_invalide(self):
        """Latitude hors [-90, 90] → 400."""
        r = self.client.post('/api/v1/places/', json={
            "title": "Bad", "description": "Y",
            "price": 50, "latitude": 999.0, "longitude": 6.0, "amenities": []
        }, headers=self._auth(self.john_token))
        self.assertEqual(r.status_code, 400)

    def test_longitude_invalide(self):
        """Longitude hors [-180, 180] → 400."""
        r = self.client.post('/api/v1/places/', json={
            "title": "Bad", "description": "Y",
            "price": 50, "latitude": 45.0, "longitude": 999.0, "amenities": []
        }, headers=self._auth(self.john_token))
        self.assertEqual(r.status_code, 400)


class TestPlacesReadUpdate(TestBase):
    """Tests lecture et modification de places."""

    def setUp(self):
        super().setUp()
        self.admin_token = self._login("admin@hbnb.io", "admin1234")
        self.john_id, self.john_token = self._create_user("john@test.com")
        _, self.jane_token = self._create_user("jane@test.com")
        self.place_id = self._create_place(self.john_token, "Loft de John")

    def test_get_place_retourne_owner_et_amenities(self):
        """GET /places/<id> retourne owner imbriqué et liste amenities."""
        r = self.client.get(f'/api/v1/places/{self.place_id}')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIn("owner", data)
        self.assertIn("amenities", data)
        self.assertIsInstance(data["amenities"], list)

    def test_get_place_inexistante(self):
        """GET place inconnue → 404."""
        r = self.client.get(
            '/api/v1/places/00000000-0000-0000-0000-000000000000')
        self.assertEqual(r.status_code, 404)

    def test_lister_toutes_les_places(self):
        """GET /places/ retourne une liste avec au moins la place de John."""
        r = self.client.get('/api/v1/places/')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)

    def test_owner_jwt_correct(self):
        """L'owner_id de la place doit correspondre à l'ID du JWT."""
        r = self.client.get(f'/api/v1/places/{self.place_id}')
        data = r.get_json()
        owner_id = data.get("owner", {}).get("id")
        self.assertEqual(owner_id, self.john_id)

    def test_proprietaire_modifie_sa_place(self):
        """Propriétaire peut modifier sa place → 200."""
        r = self.client.put(f'/api/v1/places/{self.place_id}',
                            json={"title": "Loft rénové", "price": 150},
                            headers=self._auth(self.john_token))
        self.assertEqual(r.status_code, 200)

    def test_non_proprietaire_modifie_interdit(self):
        """User non propriétaire ne peut pas modifier → 403."""
        r = self.client.put(f'/api/v1/places/{self.place_id}',
                            json={"title": "Hacked"},
                            headers=self._auth(self.jane_token))
        self.assertEqual(r.status_code, 403)

    def test_admin_modifie_place_dun_autre(self):
        """Admin peut modifier n'importe quelle place (bypass) → 200."""
        r = self.client.put(f'/api/v1/places/{self.place_id}',
                            json={"title": "Admin Edit", "price": 200},
                            headers=self._auth(self.admin_token))
        self.assertEqual(r.status_code, 200)


# =============================================================================
# SECTION 5 — REVIEWS
# =============================================================================

class TestReviewsCreate(TestBase):
    """Tests de création de reviews."""

    def setUp(self):
        super().setUp()
        self.admin_token = self._login("admin@hbnb.io", "admin1234")
        self.john_id, self.john_token = self._create_user("john@test.com")
        _, self.jane_token = self._create_user("jane@test.com")
        # John crée une place que Jane va reviewer
        self.place_id = self._create_place(self.john_token, "Loft de John")

    def test_creer_review_valide(self):
        """User reviewer une place d'un autre → 201."""
        r = self._create_review(self.jane_token, self.place_id)
        self.assertEqual(r.status_code, 201)
        data = r.get_json()
        self.assertIn("id", data)
        self.assertEqual(data["rating"], 5)

    def test_creer_sans_token(self):
        """Créer review sans token → 401."""
        r = self.client.post('/api/v1/reviews/', json={
            "text": "Super", "rating": 5, "place_id": self.place_id
        })
        self.assertEqual(r.status_code, 401)

    def test_reviewer_sa_propre_place_interdit(self):
        """Propriétaire ne peut pas reviewer sa propre place → 400."""
        r = self._create_review(self.john_token, self.place_id)
        self.assertEqual(r.status_code, 400)

    def test_doublon_review_interdit(self):
        """Même user ne peut pas laisser 2 reviews sur la même place → 400."""
        self._create_review(self.jane_token, self.place_id)
        r = self._create_review(self.jane_token, self.place_id,
                                text="Deuxième review", rating=3)
        self.assertEqual(r.status_code, 400)

    def test_rating_trop_haut(self):
        """Rating > 5 → 400."""
        r = self._create_review(self.jane_token, self.place_id, rating=10)
        self.assertEqual(r.status_code, 400)

    def test_rating_trop_bas(self):
        """Rating = 0 → 400."""
        r = self._create_review(self.jane_token, self.place_id, rating=0)
        self.assertEqual(r.status_code, 400)

    def test_place_inexistante(self):
        """Review sur une place inconnue → 404."""
        r = self._create_review(self.jane_token,
                                "00000000-0000-0000-0000-000000000000")
        self.assertIn(r.status_code, [400, 404])


class TestReviewsReadUpdateDelete(TestBase):
    """Tests lecture, modification et suppression de reviews."""

    def setUp(self):
        super().setUp()
        self.admin_token = self._login("admin@hbnb.io", "admin1234")
        self.john_id, self.john_token = self._create_user("john@test.com")
        _, self.jane_token = self._create_user("jane@test.com")
        _, self.gwen_token = self._create_user("gwen@test.com")
        self.place_id = self._create_place(self.john_token)
        # Jane crée une review sur la place de John
        r = self._create_review(self.jane_token, self.place_id)
        self.review_id = r.get_json()["id"]

    def test_get_reviews_dune_place(self):
        """GET /places/<id>/reviews retourne les reviews."""
        # Gwen ajoute aussi une review
        self._create_review(self.gwen_token, self.place_id, rating=4)
        r = self.client.get(f'/api/v1/places/{self.place_id}/reviews')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(len(data), 2)

    def test_get_reviews_place_inexistante(self):
        """GET reviews d'une place inconnue → 404."""
        r = self.client.get(
            '/api/v1/places/00000000-0000-0000-0000-000000000000/reviews')
        self.assertEqual(r.status_code, 404)

    def test_get_review_par_id(self):
        """GET /reviews/<id> retourne la review."""
        r = self.client.get(f'/api/v1/reviews/{self.review_id}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["id"], self.review_id)

    def test_get_review_inexistante(self):
        """GET review inconnue → 404."""
        r = self.client.get(
            '/api/v1/reviews/00000000-0000-0000-0000-000000000000')
        self.assertEqual(r.status_code, 404)

    def test_auteur_modifie_sa_review(self):
        """Auteur peut modifier sa review → 200."""
        r = self.client.put(f'/api/v1/reviews/{self.review_id}',
                            json={"text": "Encore mieux !", "rating": 4},
                            headers=self._auth(self.jane_token))
        self.assertEqual(r.status_code, 200)

    def test_non_auteur_modifie_interdit(self):
        """User non auteur ne peut pas modifier → 403."""
        r = self.client.put(f'/api/v1/reviews/{self.review_id}',
                            json={"text": "Hacked"},
                            headers=self._auth(self.john_token))
        self.assertEqual(r.status_code, 403)

    def test_admin_modifie_review_dun_autre(self):
        """Admin peut modifier n'importe quelle review (bypass) → 200."""
        r = self.client.put(f'/api/v1/reviews/{self.review_id}',
                            json={"text": "Admin edit", "rating": 3},
                            headers=self._auth(self.admin_token))
        self.assertEqual(r.status_code, 200)

    def test_auteur_supprime_sa_review(self):
        """Auteur peut supprimer sa review → 200."""
        r = self.client.delete(f'/api/v1/reviews/{self.review_id}',
                            headers=self._auth(self.jane_token))
        self.assertEqual(r.status_code, 200)

    def test_non_auteur_supprime_interdit(self):
        """User non auteur ne peut pas supprimer → 403."""
        r = self.client.delete(f'/api/v1/reviews/{self.review_id}',
                            headers=self._auth(self.john_token))
        self.assertEqual(r.status_code, 403)

    def test_admin_supprime_review_dun_autre(self):
        """Admin peut supprimer n'importe quelle review (bypass) → 200."""
        r = self.client.delete(f'/api/v1/reviews/{self.review_id}',
                            headers=self._auth(self.admin_token))
        self.assertEqual(r.status_code, 200)

    def test_supprimer_review_inexistante(self):
        """Supprimer une review inconnue → 404."""
        r = self.client.delete(
            '/api/v1/reviews/00000000-0000-0000-0000-000000000000',
            headers=self._auth(self.admin_token))
        self.assertEqual(r.status_code, 404)


# =============================================================================
# SECTION 6 — DELETE avec CASCADE
# =============================================================================

class TestCascadeDelete(TestBase):
    """Vérifie le comportement ON DELETE CASCADE côté API."""

    def setUp(self):
        super().setUp()
        _, self.john_token = self._create_user("john@test.com")
        _, self.jane_token = self._create_user("jane@test.com")

    def test_supprimer_place_supprime_ses_reviews(self):
        """Supprimer une place → ses reviews disparaissent (CASCADE)."""
        place_id = self._create_place(self.john_token)
        review_id = self._create_review(
            self.jane_token, place_id).get_json()["id"]

        # Supprimer la place
        self.client.delete(f'/api/v1/places/{place_id}',
                        headers=self._auth(self.john_token))

        # La review doit être inaccessible
        r = self.client.get(f'/api/v1/reviews/{review_id}')
        self.assertEqual(r.status_code, 404)

    def test_place_supprimee_retourne_404(self):
        """Après suppression, GET /places/<id> → 404."""
        place_id = self._create_place(self.jane_token)
        self.client.delete(f'/api/v1/places/{place_id}',
                        headers=self._auth(self.jane_token))
        r = self.client.get(f'/api/v1/places/{place_id}')
        self.assertEqual(r.status_code, 404)

    def test_review_supprimee_retourne_404(self):
        """Après suppression, GET /reviews/<id> → 404."""
        place_id = self._create_place(self.john_token)
        review_id = self._create_review(
            self.jane_token, place_id).get_json()["id"]
        self.client.delete(f'/api/v1/reviews/{review_id}',
                        headers=self._auth(self.jane_token))
        r = self.client.get(f'/api/v1/reviews/{review_id}')
        self.assertEqual(r.status_code, 404)

    def test_reviews_place_inexistante_404(self):
        """GET /places/bad_id/reviews → 404."""
        r = self.client.get(
            '/api/v1/places/00000000-0000-0000-0000-000000000000/reviews')
        self.assertEqual(r.status_code, 404)


# =============================================================================
# SECTION 7 — RBAC complet
# =============================================================================

class TestRBAC(TestBase):
    """Tests du contrôle d'accès par rôle."""

    def setUp(self):
        super().setUp()
        self.admin_token = self._login("admin@hbnb.io", "admin1234")
        self.john_id, self.john_token = self._create_user("john@test.com")
        _, self.jane_token = self._create_user("jane@test.com")
        self.amenity_id = self._create_amenity("Pool")
        self.place_id = self._create_place(self.john_token)

    def test_user_normal_cree_user_interdit(self):
        """User normal ne peut pas créer un autre user → 403."""
        r = self.client.post('/api/v1/users/', json={
            "first_name": "X", "last_name": "Y",
            "email": "hack@test.com", "password": "pass1234"
        }, headers=self._auth(self.john_token))
        self.assertEqual(r.status_code, 403)

    def test_user_normal_cree_amenity_interdit(self):
        """User normal ne peut pas créer une amenity → 403."""
        r = self.client.post('/api/v1/amenities/',
                            json={"name": "Unauthorized"},
                            headers=self._auth(self.john_token))
        self.assertEqual(r.status_code, 403)

    def test_user_normal_modifie_amenity_interdit(self):
        """User normal ne peut pas modifier une amenity → 403."""
        r = self.client.put(f'/api/v1/amenities/{self.amenity_id}',
                            json={"name": "Hacked"},
                            headers=self._auth(self.john_token))
        self.assertEqual(r.status_code, 403)

    def test_admin_bypass_ownership_place(self):
        """Admin peut modifier une place qu'il ne possède pas → 200."""
        r = self.client.put(f'/api/v1/places/{self.place_id}',
                            json={"title": "Admin Edit", "price": 999},
                            headers=self._auth(self.admin_token))
        self.assertEqual(r.status_code, 200)

    def test_admin_bypass_ownership_review(self):
        """Admin peut supprimer une review qu'il n'a pas écrite → 200."""
        review_id = self._create_review(
            self.jane_token, self.place_id).get_json()["id"]
        r = self.client.delete(f'/api/v1/reviews/{review_id}',
                            headers=self._auth(self.admin_token))
        self.assertEqual(r.status_code, 200)


if __name__ == "__main__":
    unittest.main(verbosity=2)