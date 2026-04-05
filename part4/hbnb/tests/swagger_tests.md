# HBnB — Guide de Tests Swagger
## Organisés par type : Auth, CRUD, RBAC, Relations, DELETE

---

## Accès à Swagger

1. Lancer le serveur :
```bash
python3 run.py
```
2. Ouvrir dans le navigateur :
```
http://127.0.0.1:5000/api/v1/
```

---

## Comment utiliser le token JWT dans Swagger

1. Faire `POST /api/v1/auth/login` et copier le `access_token`
2. Cliquer sur **Authorize** en haut à droite
3. Saisir `Bearer <token>` dans le champ Value
4. Cliquer **Authorize** puis **Close**

> Le token expire après **1 heure**. Si vous obtenez `401 Token has expired`, refaites le login.

---

## IDs utiles (données initiales)

| Donnée | ID |
|---|---|
| Admin | `36c9050e-ddd3-4c3b-9731-9f487208bbc1` |
| WiFi | `7c9fdf4d-99be-4b1c-8c2e-5aea5db0d0eb` |
| Swimming Pool | `ae5ae8a5-0203-451b-9cb8-6086e5b2f41e` |
| Air Conditioning | `97bc1cc5-3dcd-439e-894f-e9986dedd012` |

---

## ============================================================
## SECTION 1 — AUTH
## ============================================================

### TEST 1.1 — Login admin valide
**Endpoint :** `POST /api/v1/auth/login`
```json
{ "email": "admin@hbnb.io", "password": "admin1234" }
```
**Attendu :** `200` + `access_token`
> Sauvegarder le token et l'utiliser dans Authorize.

---

### TEST 1.2 — Login mauvais mot de passe
**Endpoint :** `POST /api/v1/auth/login`
```json
{ "email": "admin@hbnb.io", "password": "mauvais_mdp" }
```
**Attendu :** `401 Invalid credentials`

---

### TEST 1.3 — Login email inexistant
**Endpoint :** `POST /api/v1/auth/login`
```json
{ "email": "inexistant@test.com", "password": "admin1234" }
```
**Attendu :** `401 Invalid credentials`

---

### TEST 1.4 — Accès endpoint protégé sans token
Cliquer Authorize → Logout (enlever le token)

**Endpoint :** `POST /api/v1/users/`
```json
{ "first_name": "Test", "last_name": "User", "email": "t@t.com", "password": "pass123" }
```
**Attendu :** `401 Missing Authorization Header`

---

### TEST 1.5 — Accès endpoint protégé avec token valide
Se reconnecter avec le token admin dans Authorize.

**Endpoint :** `POST /api/v1/amenities/`
```json
{ "name": "Sauna", "description": "Sauna privé" }
```
**Attendu :** `201` avec l'id de la nouvelle amenity

---

## ============================================================
## SECTION 2 — CRUD : USERS
## ============================================================

> Token admin requis pour POST et DELETE.
> Sauvegarder les IDs créés pour les tests suivants.

### TEST 2.1 — Créer un user valide (John)
**Endpoint :** `POST /api/v1/users/`
**Token :** Admin
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@test.com",
  "password": "password123"
}
```
**Attendu :** `201` + `{ "id": "...", "first_name": "John", ... }`
> Sauvegarder `john_id`.

---

### TEST 2.2 — Créer un deuxième user (Jane)
**Endpoint :** `POST /api/v1/users/`
**Token :** Admin
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane@test.com",
  "password": "password123"
}
```
**Attendu :** `201`
> Sauvegarder `jane_id`.

---

### TEST 2.3 — Email dupliqué
```json
{ "first_name": "Dup", "last_name": "User", "email": "john@test.com", "password": "pass123" }
```
**Attendu :** `422 Email already exists`

---

### TEST 2.4 — Lire tous les users
**Endpoint :** `GET /api/v1/users/`
**Token :** non requis
**Attendu :** `200` liste avec 3 users (admin + John + Jane)

---

### TEST 2.5 — Lire un user par ID
**Endpoint :** `GET /api/v1/users/{john_id}`
**Attendu :** `200` + données de John

---

### TEST 2.6 — User inexistant
**Endpoint :** `GET /api/v1/users/00000000-0000-0000-0000-000000000000`
**Attendu :** `404 User not found`

---

### TEST 2.7 — Modifier son propre profil
**Endpoint :** `PUT /api/v1/users/{john_id}`
**Token :** John
```json
{ "first_name": "Johnny", "last_name": "Doe" }
```
**Attendu :** `200`

---

### TEST 2.8 — Modifier profil d'un autre (non admin)
**Endpoint :** `PUT /api/v1/users/{jane_id}`
**Token :** John
```json
{ "first_name": "Hacked" }
```
**Attendu :** `403 Unauthorized action`

---

### TEST 2.9 — Modifier email (interdit pour user normal)
**Endpoint :** `PUT /api/v1/users/{john_id}`
**Token :** John
```json
{ "email": "newemail@test.com" }
```
**Attendu :** `400 You cannot modify email or password`

---

### TEST 2.10 — Admin modifie n'importe quel user
**Endpoint :** `PUT /api/v1/users/{john_id}`
**Token :** Admin
```json
{ "first_name": "John", "email": "john.new@test.com" }
```
**Attendu :** `200` (bypass ownership)

---

## ============================================================
## SECTION 3 — CRUD : AMENITIES
## ============================================================

### TEST 3.1 — Créer amenity valide (admin)
**Endpoint :** `POST /api/v1/amenities/`
**Token :** Admin
```json
{ "name": "Jacuzzi", "description": "Jacuzzi privé de luxe" }
```
**Attendu :** `201`
> Sauvegarder `amenity_id`.

---

### TEST 3.2 — Créer amenity sans être admin
**Token :** John
**Attendu :** `403 Admin privileges required`

---

### TEST 3.3 — Créer amenity sans token
**Attendu :** `401 Missing Authorization Header`

---

### TEST 3.4 — Lire toutes les amenities
**Endpoint :** `GET /api/v1/amenities/`
**Attendu :** `200` (au moins WiFi, Swimming Pool, Air Conditioning + Jacuzzi)

---

### TEST 3.5 — Lire amenity par ID
**Endpoint :** `GET /api/v1/amenities/{amenity_id}`
**Attendu :** `200 Jacuzzi`

---

### TEST 3.6 — Amenity inexistante
**Endpoint :** `GET /api/v1/amenities/00000000-0000-0000-0000-000000000000`
**Attendu :** `404 Amenity not found`

---

### TEST 3.7 — Modifier amenity (admin)
**Endpoint :** `PUT /api/v1/amenities/{amenity_id}`
**Token :** Admin
```json
{ "name": "Jacuzzi VIP", "description": "Jacuzzi privé avec jets massants" }
```
**Attendu :** `200 Amenity updated successfully`

---

### TEST 3.8 — Modifier amenity sans être admin
**Token :** John
**Attendu :** `403 Admin privileges required`

---

## ============================================================
## SECTION 4 — CRUD : PLACES
## ============================================================

### TEST 4.1 — Créer place valide (John)
**Endpoint :** `POST /api/v1/places/`
**Token :** John
```json
{
  "title": "Appartement Paris",
  "description": "Bel appartement",
  "price": 120.00,
  "latitude": 48.8566,
  "longitude": 2.3522,
  "amenities": ["7c9fdf4d-99be-4b1c-8c2e-5aea5db0d0eb"]
}
```
**Attendu :** `201` + `owner_id` = `john_id`
> Sauvegarder `place_id`.

---

### TEST 4.2 — Prix négatif
```json
{ "title": "Bad", "price": -50.0, "latitude": 48.0, "longitude": 2.0, "amenities": [] }
```
**Attendu :** `400 price must be greater than 0`

---

### TEST 4.3 — Latitude invalide
```json
{ "title": "Bad", "price": 50.0, "latitude": 999.0, "longitude": 2.0, "amenities": [] }
```
**Attendu :** `400`

---

### TEST 4.4 — Place sans token
**Attendu :** `401`

---

### TEST 4.5 — Lire toutes les places
**Endpoint :** `GET /api/v1/places/`
**Attendu :** `200` (vue réduite : id, title, latitude, longitude)

---

### TEST 4.6 — Lire place par ID (owner + amenities imbriqués)
**Endpoint :** `GET /api/v1/places/{place_id}`
**Attendu :** `200` avec objet `owner` et liste `amenities`

---

### TEST 4.7 — Place inexistante
**Endpoint :** `GET /api/v1/places/00000000-0000-0000-0000-000000000000`
**Attendu :** `404 Place not found`

---

### TEST 4.8 — Modifier sa propre place
**Endpoint :** `PUT /api/v1/places/{place_id}`
**Token :** John
```json
{ "title": "Appartement Paris Rénové", "price": 150.00 }
```
**Attendu :** `200 Place updated successfully`

---

### TEST 4.9 — Modifier la place d'un autre (non admin)
**Endpoint :** `PUT /api/v1/places/{place_id}`
**Token :** Jane
**Attendu :** `403 Unauthorized action`

---

### TEST 4.10 — Lire les reviews d'une place
**Endpoint :** `GET /api/v1/places/{place_id}/reviews`
**Attendu :** `200` liste (vide si aucune review)

---

## ============================================================
## SECTION 5 — CRUD : REVIEWS
## ============================================================

> Créer d'abord `john_token` et `jane_token` via `POST /auth/login`.

### TEST 5.1 — Créer review valide (Jane sur place de John)
**Endpoint :** `POST /api/v1/reviews/`
**Token :** Jane
```json
{
  "text": "Super endroit, très bien situé !",
  "rating": 5,
  "place_id": "<place_id>"
}
```
**Attendu :** `201` + `user_id` = `jane_id`
> Sauvegarder `review_id`.

---

### TEST 5.2 — Review sur sa propre place
**Token :** John
```json
{ "text": "Ma place est top", "rating": 5, "place_id": "<place_id>" }
```
**Attendu :** `400 You cannot review your own place`

---

### TEST 5.3 — Doublon review (Jane a déjà reviewé)
**Token :** Jane
**Attendu :** `400 You have already reviewed this place`

---

### TEST 5.4 — Rating invalide
```json
{ "text": "Bad", "rating": 10, "place_id": "<place_id>" }
```
**Attendu :** `400 Rating must be between 1 and 5`

---

### TEST 5.5 — Review sans token
**Attendu :** `401`

---

### TEST 5.6 — Lire toutes les reviews
**Endpoint :** `GET /api/v1/reviews/`
**Attendu :** `200` liste

---

### TEST 5.7 — Lire review par ID
**Endpoint :** `GET /api/v1/reviews/{review_id}`
**Attendu :** `200` + text + rating + user_id + place_id

---

### TEST 5.8 — Lire reviews d'une place
**Endpoint :** `GET /api/v1/places/{place_id}/reviews`
**Attendu :** `200` liste avec user_id et place_id dans chaque item

---

### TEST 5.9 — Reviews d'une place inexistante
**Endpoint :** `GET /api/v1/places/00000000-0000-0000-0000-000000000000/reviews`
**Attendu :** `404 Place not found`

---

### TEST 5.10 — Modifier sa propre review
**Endpoint :** `PUT /api/v1/reviews/{review_id}`
**Token :** Jane
```json
{ "text": "Encore mieux que prévu !", "rating": 5 }
```
**Attendu :** `200 Review updated successfully`

---

### TEST 5.11 — Modifier review d'un autre (non admin)
**Endpoint :** `PUT /api/v1/reviews/{review_id}`
**Token :** John
**Attendu :** `403 Unauthorized action`

---

### TEST 5.12 — Supprimer review inexistante
**Endpoint :** `DELETE /api/v1/reviews/00000000-0000-0000-0000-000000000000`
**Token :** Admin
**Attendu :** `404 Review not found`

---

### TEST 5.13 — Supprimer review d'un autre (non admin)
**Endpoint :** `DELETE /api/v1/reviews/{review_id}`
**Token :** John
**Attendu :** `403 Unauthorized action`

---

### TEST 5.14 — Supprimer sa propre review
**Endpoint :** `DELETE /api/v1/reviews/{review_id}`
**Token :** Jane
**Attendu :** `200 Review deleted successfully`

---

## ============================================================
## SECTION 6 — RBAC
## ============================================================

### TEST 6.1 — Admin crée un user
**Endpoint :** `POST /api/v1/users/`
**Token :** Admin
**Attendu :** `201`

---

### TEST 6.2 — User normal crée un user
**Token :** John
**Attendu :** `403 Admin privileges required`

---

### TEST 6.3 — Admin modifie le profil d'un autre (bypass)
**Endpoint :** `PUT /api/v1/users/{john_id}`
**Token :** Admin
```json
{ "first_name": "Modifié par Admin" }
```
**Attendu :** `200`

---

### TEST 6.4 — User normal crée une amenity
**Token :** John
**Attendu :** `403 Admin privileges required`

---

### TEST 6.5 — Admin crée une amenity
**Token :** Admin
**Attendu :** `201`

---

### TEST 6.6 — Admin modifie la place d'un autre (bypass)
**Endpoint :** `PUT /api/v1/places/{place_id}`
**Token :** Admin
```json
{ "title": "Modifié par Admin", "price": 200.00 }
```
**Attendu :** `200`

---

### TEST 6.7 — Admin modifie une amenity
**Endpoint :** `PUT /api/v1/amenities/{amenity_id}`
**Token :** Admin
**Attendu :** `200`

---

### TEST 6.8 — Admin supprime la review d'un autre (bypass)
Créer d'abord une review de Jane, puis :
**Endpoint :** `DELETE /api/v1/reviews/{review_id}`
**Token :** Admin
**Attendu :** `200 Review deleted successfully`

---

## ============================================================
## SECTION 7 — RELATIONS
## ============================================================

### TEST 7.1 — GET place retourne owner imbriqué
**Endpoint :** `GET /api/v1/places/{place_id}`
**Attendu :** `200` avec champ `owner` contenant `id`, `first_name`, `last_name`, `email`

---

### TEST 7.2 — GET place retourne amenities imbriquées
**Endpoint :** `GET /api/v1/places/{place_id}`
**Attendu :** `200` avec champ `amenities` (liste d'objets `{id, name}`)

---

### TEST 7.3 — owner_id = ID du user connecté (JWT)
Comparer le `owner.id` dans la réponse GET avec le `john_id` sauvegardé.
**Attendu :** IDs identiques — owner_id extrait du JWT, jamais du body

---

### TEST 7.4 — Reviews d'une place retournent user_id et place_id
**Endpoint :** `GET /api/v1/places/{place_id}/reviews`
**Attendu :** Chaque review contient `user_id` et `place_id`

---

### TEST 7.5 — Reviews place inexistante
**Endpoint :** `GET /api/v1/places/00000000-0000-0000-0000-000000000000/reviews`
**Attendu :** `404 Place not found`

---

## ============================================================
## SECTION 8 — DELETE : Users, Places, Amenities
## ============================================================

> Cette section teste les nouveaux endpoints DELETE pour les entités users, places et amenities.

---

### TEST 8.1 — User normal supprime un user → 403
**Endpoint :** `DELETE /api/v1/users/{john_id}`
**Token :** John (non-admin)
**Attendu :** `403 Admin privileges required`

---

### TEST 8.2 — Admin se supprime lui-même → 400
**Endpoint :** `DELETE /api/v1/users/{admin_id}`
**Token :** Admin
> Récupérer l'admin_id via `GET /api/v1/users/` en cherchant `email = admin@hbnb.io`
**Attendu :** `400 Cannot delete your own admin account`

---

### TEST 8.3 — DELETE user inexistant → 404
**Endpoint :** `DELETE /api/v1/users/00000000-0000-0000-0000-000000000000`
**Token :** Admin
**Attendu :** `404 User not found`

---

### TEST 8.4 — Non-propriétaire supprime une place → 403
**Endpoint :** `DELETE /api/v1/places/{place_id}`
**Token :** Jane (non propriétaire)
**Attendu :** `403 Unauthorized action`

---

### TEST 8.5 — DELETE place inexistante → 404
**Endpoint :** `DELETE /api/v1/places/00000000-0000-0000-0000-000000000000`
**Token :** Admin
**Attendu :** `404 Place not found`

---

### TEST 8.6 — User normal supprime une amenity → 403
**Endpoint :** `DELETE /api/v1/amenities/{amenity_id}`
**Token :** John
**Attendu :** `403 Admin privileges required`

---

### TEST 8.7 — DELETE amenity inexistante → 404
**Endpoint :** `DELETE /api/v1/amenities/00000000-0000-0000-0000-000000000000`
**Token :** Admin
**Attendu :** `404 Amenity not found`

---

### TEST 8.8 — Admin supprime une amenity → 200
Créer d'abord une amenity temporaire `POST /api/v1/amenities/` → `{ "name": "Temp Delete" }`, puis :

**Endpoint :** `DELETE /api/v1/amenities/{temp_amenity_id}`
**Token :** Admin
**Attendu :** `200 Amenity deleted successfully`
**Vérifier :** `GET /api/v1/amenities/{temp_amenity_id}` → `404`

---

### TEST 8.9 — Propriétaire supprime sa place → 200 (+ CASCADE reviews)
Créer une place temporaire avec John, créer une review de Jane dessus, puis :

**Endpoint :** `DELETE /api/v1/places/{temp_place_id}`
**Token :** John
**Attendu :** `200 Place deleted successfully`
**Vérifier :** `GET /api/v1/places/{temp_place_id}` → `404`
> **CASCADE** : la review de Jane sur cette place est automatiquement supprimée.

---

### TEST 8.10 — Admin supprime un user → 200 (+ CASCADE places + reviews)
Créer un user temporaire `POST /api/v1/users/` → `{ "email": "temp@test.com", ... }`, puis :

**Endpoint :** `DELETE /api/v1/users/{temp_user_id}`
**Token :** Admin
**Attendu :** `200 User successfully deleted`
**Vérifier :** `GET /api/v1/users/{temp_user_id}` → `404`
> **CASCADE** : si cet utilisateur avait des places et des reviews, elles sont toutes supprimées automatiquement.

---

## Récapitulatif des codes HTTP des endpoints DELETE

| Entité | Condition | Code |
|---|---|---|
| User | Admin, user existant, pas soi-même | `200` ✅ |
| User | Non-admin | `403` ❌ |
| User | Admin, user inexistant | `404` ❌ |
| User | Admin, suppression de son propre compte | `400` ❌ |
| Place | Propriétaire ou Admin, place existante | `200` ✅ |
| Place | Ni propriétaire ni Admin | `403` ❌ |
| Place | Place inexistante | `404` ❌ |
| Place | Sans token | `401` ❌ |
| Amenity | Admin, amenity existante | `200` ✅ |
| Amenity | Non-admin | `403` ❌ |
| Amenity | Amenity inexistante | `404` ❌ |
| Amenity | Sans token | `401` ❌ |
| Review | Auteur ou Admin, review existante | `200` ✅ |
| Review | Ni auteur ni Admin | `403` ❌ |
| Review | Review inexistante | `404` ❌ |
| Review | Sans token | `401` ❌ |

---

_Auteurs : **Sara Rebati · Valentin Planchon · Damien Rossi** — Holberton School 2026_