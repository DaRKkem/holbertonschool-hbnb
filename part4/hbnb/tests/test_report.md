# HBnB — Rapport de Tests
**Date :** Avril 2026
**Testeurs :** Sara Rebati · Valentin Planchon · Damien Rossi
**Version :** Part 3 — Hbnb

---

## Environnement de test

| Propriété | Valeur |
|---|---|
| OS | Ubuntu 24.04 |
| Python | 3.12 |
| Flask | 3.x |
| Flask-RESTx | 1.3.x |
| Flask-JWT-Extended | 4.x |
| Flask-Bcrypt | 1.x |
| SQLAlchemy | 2.x |
| DB | `instance/development.db` |
| Outil SQL | `sqlite3` |
| URL API | `http://127.0.0.1:5000/api/v1/` |

---

## SECTION 1 — AUTH

| ID | Test | Attendu | Obtenu | Status |
|---|---|---|---|---|
| 1.1 | Login admin valide | `200` + token | `200` + access_token | ✅ |
| 1.2 | Login mauvais mot de passe | `401` | `401` Invalid credentials | ✅ |
| 1.3 | Login email inexistant | `401` | `401` Invalid credentials | ✅ |
| 1.4 | Accès protégé sans token | `401` | `401` Missing Authorization Header | ✅ |
| 1.5 | Accès protégé avec token valide | `201` | `201` amenity créée | ✅ |

---

## SECTION 2 — CRUD : USERS

| ID | Test | Attendu | Obtenu | Status |
|---|---|---|---|---|
| 2.1 | Créer user valide (John) | `201` | `201` + id | ✅ |
| 2.2 | Créer deuxième user (Jane) | `201` | `201` + id | ✅ |
| 2.3 | Email dupliqué | `422` | `422` Email already exists | ✅ |
| 2.4 | Login John et Jane (tokens) | tokens obtenus | tokens obtenus | ✅ |
| 2.5 | Lire tous les users | `200` (3 users) | `200` liste | ✅ |
| 2.6 | Lire user par ID | `200` + first_name | `200` John | ✅ |
| 2.7 | Lire user inexistant | `404` | `404` User not found | ✅ |
| 2.8 | Modifier son propre profil | `200` | `200` mis à jour | ✅ |
| 2.9 | Modifier profil d'un autre | `403` | `403` Unauthorized action | ✅ |
| 2.10 | Modifier email via PUT /users | `400` | `400` cannot modify email | ✅ |

---

## SECTION 3 — CRUD : AMENITIES

| ID | Test | Attendu | Obtenu | Status |
|---|---|---|---|---|
| 3.1 | Créer amenity valide (admin) | `201` | `201` Jacuzzi | ✅ |
| 3.2 | Créer amenity sans être admin | `403` | `403` Admin privileges required | ✅ |
| 3.3 | Créer amenity sans token | `401` | `401` Missing Authorization Header | ✅ |
| 3.4 | Lire toutes les amenities | `200` | `200` liste | ✅ |
| 3.5 | Lire amenity par ID | `200` | `200` Jacuzzi | ✅ |
| 3.6 | Lire amenity inexistante | `404` | `404` Amenity not found | ✅ |
| 3.7 | Modifier amenity (admin) | `200` | `200` mise à jour | ✅ |
| 3.8 | Modifier amenity sans être admin | `403` | `403` Admin privileges required | ✅ |

---

## SECTION 4 — CRUD : PLACES

| ID | Test | Attendu | Obtenu | Status |
|---|---|---|---|---|
| 4.1 | Créer place valide (John) | `201` | `201` + owner_id | ✅ |
| 4.2 | Prix négatif | `400` | `400` price must be greater than 0 | ✅ |
| 4.3 | Latitude invalide | `400` | `400` latitude out of range | ✅ |
| 4.4 | Créer place sans token | `401` | `401` Missing Authorization Header | ✅ |
| 4.5 | Lire toutes les places | `200` | `200` liste | ✅ |
| 4.6 | Lire place par ID (owner + amenities) | `200` + imbriqués | `200` owner + amenities | ✅ |
| 4.7 | Lire place inexistante | `404` | `404` Place not found | ✅ |
| 4.8 | Modifier sa propre place | `200` | `200` mis à jour | ✅ |
| 4.9 | Modifier place d'un autre | `403` | `403` Unauthorized action | ✅ |

---

## SECTION 5 — CRUD : REVIEWS

| ID | Test | Attendu | Obtenu | Status |
|---|---|---|---|---|
| 5.1 | Créer review valide (Jane sur place de John) | `201` | `201` + id | ✅ |
| 5.2 | Review sur sa propre place | `400` | `400` cannot review your own place | ✅ |
| 5.3 | Doublon review | `400` | `400` already reviewed | ✅ |
| 5.4 | Rating invalide (10) | `400` | `400` rating must be between 1 and 5 | ✅ |
| 5.5 | Créer review sans token | `401` | `401` Missing Authorization Header | ✅ |
| 5.6 | Lire toutes les reviews | `200` | `200` liste | ✅ |
| 5.7 | Lire review par ID | `200` | `200` + text + rating | ✅ |
| 5.8 | Lire reviews d'une place | `200` | `200` liste reviews | ✅ |
| 5.9 | Reviews place inexistante | `404` | `404` Place not found | ✅ |
| 5.10 | Modifier sa propre review | `200` | `200` mis à jour | ✅ |
| 5.11 | Modifier review d'un autre | `403` | `403` Unauthorized action | ✅ |
| 5.12 | Supprimer review inexistante | `404` | `404` Review not found | ✅ |
| 5.13 | Supprimer review d'un autre (non admin) | `403` | `403` Unauthorized action | ✅ |
| 5.14 | Supprimer sa propre review | `200` | `200` deleted successfully | ✅ |

---

## SECTION 6 — RBAC

| ID | Test | Attendu | Obtenu | Status |
|---|---|---|---|---|
| 6.1 | Admin crée un user | `201` | `201` | ✅ |
| 6.2 | User normal crée un user | `403` | `403` Admin privileges required | ✅ |
| 6.3 | Admin modifie user d'un autre | `200` (bypass) | `200` | ✅ |
| 6.4 | User normal crée une amenity | `403` | `403` Admin privileges required | ✅ |
| 6.5 | Admin crée une amenity | `201` | `201` | ✅ |
| 6.6 | Admin modifie place d'un autre | `200` (bypass) | `200` | ✅ |
| 6.7 | Admin modifie une amenity | `200` | `200` | ✅ |
| 6.8 | Admin supprime review d'un autre | `200` (bypass) | `200` | ✅ |

---

## SECTION 7 — RELATIONS

| ID | Test | Attendu | Obtenu | Status |
|---|---|---|---|---|
| 7.1 | GET place retourne owner imbriqué | `200` + owner | `200` owner complet | ✅ |
| 7.2 | GET place retourne amenities imbriquées | `200` + amenities | `200` liste amenities | ✅ |
| 7.3 | GET reviews retourne user_id et place_id | `200` + ids | `200` + user_id + place_id | ✅ |
| 7.4 | Reviews place inexistante | `404` | `404` Place not found | ✅ |
| 7.5 | owner_id = ID du user connecté (JWT) | IDs identiques | IDs identiques | ✅ |

---

## SECTION 8 — DELETE : Users, Places, Amenities

| ID | Test | Attendu | Obtenu | Status |
|---|---|---|---|---|
| 8.1 | User normal supprime un user | `403` | `403` Admin privileges required | ✅ |
| 8.2 | Admin se supprime lui-même | `400` | `400` Cannot delete your own admin account | ✅ |
| 8.3 | DELETE user inexistant | `404` | `404` User not found | ✅ |
| 8.4 | Non-propriétaire supprime une place | `403` | `403` Unauthorized action | ✅ |
| 8.5 | DELETE place inexistante | `404` | `404` Place not found | ✅ |
| 8.6 | User normal supprime une amenity | `403` | `403` Admin privileges required | ✅ |
| 8.7 | DELETE amenity inexistante | `404` | `404` Amenity not found | ✅ |
| 8.8 | Admin supprime une amenity | `200` | `200` Amenity deleted successfully | ✅ |
| 8.9 | Propriétaire supprime sa place | `200` | `200` Place deleted successfully | ✅ |
| 8.10 | Place supprimée bien absente | `404` | `404` Place not found | ✅ |
| 8.11 | Admin supprime un user | `200` | `200` User successfully deleted | ✅ |

---

## SECTION DB — Tests SQL (run_tests.py)

```bash
python3 tests/run_tests.py
```

| Section | Tests | Passés | Échoués |
|---|---|---|---|
| 0 — Données initiales | 6 | 6 | 0 |
| 1 — CRUD Users | 10 | 10 | 0 |
| 2 — CRUD Amenities | 6 | 6 | 0 |
| 3 — CRUD Places | 11 | 11 | 0 |
| 4 — CRUD Reviews | 11 | 11 | 0 |
| 5 — Relations | 12 | 12 | 0 |
| 6 — RBAC | 5 | 5 | 0 |
| 7 — Suppression ordonnée | 4 | 4 | 0 |
| Final | 6 | 6 | 0 |
| **TOTAL** | **71** | **71** | **0** |

---

## Bugs identifiés et corrigés

| ID | Description | Fichier | Statut |
|---|---|---|---|
| B-01 | Swagger inaccessible sur `/api/v1/` (404) | `app/api/v1/__init__.py` | ✅ Corrigé — `doc="/v1/"` |
| B-02 | `delete_place()` manquant dans facade.py | `app/services/facade.py` | ✅ Corrigé — méthode ajoutée |
| B-03 | Pas d'endpoint DELETE pour users/places/amenities | `users.py`, `places.py`, `amenities.py` | ✅ Corrigé — DELETE implémenté |
| B-04 | Tests 3.10/5.5/5.6 attendaient RESTRICT (Traceback) | `tests/run_tests.py` | ✅ Corrigé — adaptés au CASCADE |

---

## Conclusion

| Catégorie | Résultat |
|---|---|
| Auth (JWT) | ✅ Fonctionnel — login, token, expiry 1h |
| CRUD complet | ✅ Toutes entités : GET/POST/PUT/DELETE |
| RBAC | ✅ Admin / Owner / Public correctement séparés |
| Relations | ✅ Owner + amenities imbriqués dans GET place |
| Intégrité DB | ✅ CASCADE, UNIQUE, CHECK tous fonctionnels |
| Endpoints DELETE | ✅ Users (admin), Places (owner/admin), Amenities (admin), Reviews (auteur/admin) |
| **Bilan global** | ✅ **70/70 API — 71/71 DB — 0 régression** |