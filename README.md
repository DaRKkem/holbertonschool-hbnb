# HBnB Evolution

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-lightgrey)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red)
![JWT](https://img.shields.io/badge/JWT-Authentication-orange)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow)
![HTML5](https://img.shields.io/badge/HTML5-semantic-orange)
![License](https://img.shields.io/badge/License-Holberton-yellow)

## Overview

**HBnB Evolution** is a simplified AirBnB-like application built progressively over 4 parts, from architecture design to a fully functional full-stack web application.

The project covers the entire lifecycle of a software product: technical documentation, backend API, database persistence, authentication, and a dynamic web client — all following industry best practices in software engineering.

---

## Authors

| Name | GitHub |
|---|---|
| Sara Rebati | [@saraestelle](https://github.com/saraestelle) |
| Valentin Planchon | [@valentinplanchon](https://github.com/valentinplanchon) |
| Damien Rossi | [@DaRKkem](https://github.com/DaRKkem) |

Holberton School — 2026

---

## Project Structure

```
holbertonschool-hbnb/
├── README.md          ← this file
├── part1/             ← Technical Documentation (UML, architecture)
├── part2/             ← Business Logic & REST API (in-memory)
├── part3/             ← Authentication & Database Persistence
└── part4/             ← Simple Web Client (HTML/CSS/JS)
```

Each part builds on the previous one and represents a key milestone in the evolution of the application.

---

## Part 1 — Technical Documentation

### Goal
Design the full system architecture and document it before writing any code.

### Key Topics
- 3-layer architecture (Presentation / Business Logic / Persistence)
- Facade design pattern
- UML diagrams:
  - High-level package diagram
  - Class diagram (Business Logic Layer)
  - Sequence diagrams for key API calls (user registration, place creation, review submission, fetch places)

### Structure
```
part1/
├── task_0/   ← High-level package diagram
├── task_1/   ← Class diagram for Business Logic Layer
├── task_2/   ← Sequence diagrams for API calls
├── task_3/   ← Full technical documentation (Markdown + PDF)
└── assets/
```

### Outcome
A complete technical blueprint serving as the specification for Parts 2, 3 and 4.

---

## Part 2 — Business Logic & API Endpoints

### Goal
Implement the core business logic and expose a RESTful API. No database yet — data is stored in memory.

### Stack
- Python 3.12
- Flask + flask-restx
- In-memory repository
- Swagger UI (auto-generated)

### Entities
- `User` — with email validation, password hashing (SHA-256), bidirectional relations
- `Place` — with owner, amenities, price/coordinates validation
- `Review` — with rating (1–5), anti-self-review rule
- `Amenity` — linked to places

### API Endpoints

| Resource | POST | GET all | GET by ID | PUT | DELETE |
|---|---|---|---|---|---|
| Users | ✅ 201 | ✅ 200 | ✅ 200 | ✅ 200 | ❌ |
| Places | ✅ 201 | ✅ 200 | ✅ 200 | ✅ 200 | ❌ |
| Reviews | ✅ 201 | ✅ 200 | ✅ 200 | ✅ 200 | ✅ 200 |
| Amenities | ✅ 201 | ✅ 200 | ✅ 200 | ✅ 200 | ❌ |

### Tests
- 54 unit tests (`unittest`) — 52 pass, 2 expected failures (documented)
- Full isolation via `facade.reset()` in `setUp`

### Running
```bash
cd part2/hbnb
pip install -r requirements.txt
python3 run.py
# Swagger → http://127.0.0.1:5000/api/v1/
```

---

## Part 3 — Authentication & Database Persistence

### Goal
Replace the in-memory store with a real SQLite database and add JWT authentication with role-based access control (RBAC).

### Stack
- Flask + flask-restx
- SQLAlchemy ORM
- Flask-JWT-Extended
- Flask-Bcrypt
- SQLite (`instance/development.db`)

### New Features vs Part 2
- JWT login via `POST /api/v1/auth/login`
- Passwords hashed with **bcrypt** (replacing SHA-256)
- Full RBAC: admin vs regular user permissions
- SQLAlchemy models with FK constraints, CASCADE rules, UNIQUE constraints
- `schema.sql` + `initial_data.sql` for clean DB setup and seeding
- 4 test suites: HTTP API (59), DB Python (68), SQL direct, unit tests (63)

### Default Credentials

| Field | Value |
|---|---|
| Admin email | `admin@hbnb.io` |
| Admin password | `admin1234` |

### RBAC Summary

| Action | No token | Regular user | Admin |
|---|---|---|---|
| Create user | 401 | 403 | 201 |
| Create amenity | 401 | 403 | 201 |
| Create place | 401 | 201 | 201 |
| Create review | 401 | 201 | 201 |
| Update own resource | 401 | 200 | 200 |
| Update other's resource | 401 | 403 | 200 |

### Running
```bash
cd part3/hbnb
pip install -r requirements.txt
sqlite3 instance/development.db < schema.sql
sqlite3 instance/development.db < initial_data.sql
python3 run.py
# Swagger → http://127.0.0.1:5000/api/v1/
```

---

## Part 4 — Simple Web Client

### Goal
Build a dynamic front-end that connects to the Part 3 Flask API using vanilla JavaScript ES6, HTML5 and CSS3.

### Stack
- HTML5 (semantic)
- CSS3 (custom properties, responsive grid)
- JavaScript ES6 (Fetch API, cookies, DOM manipulation)
- No framework, no build tool

### Pages

| Page | Description |
|---|---|
| `index.html` | List of all places with client-side price filter |
| `login.html` | Login form — stores JWT in cookie on success |
| `place.html` | Place details, amenities, reviews, inline review form |
| `add_review.html` | Standalone review form (auth required) |

### Features
- JWT token stored in browser cookie after login
- Login button shown/hidden based on authentication state
- Places fetched from API and filtered client-side (no reload)
- Place details and reviews loaded dynamically from API
- Review submission with success/error feedback
- Unauthenticated users redirected from protected pages

### Running
```bash
# 1. Start Flask back-end (from part4/hbnb)
python3 run.py

# 2. Open index.html with Live Server (port 5500)
# or any static file server
```

> Make sure CORS is configured in `app/__init__.py`:
> ```python
> CORS(app, resources={r"/api/*": {"origins": "*"}})
> app.url_map.strict_slashes = False
> ```

---

## Full Stack Overview

```
┌─────────────────────────────────────────────┐
│           Part 4 — Web Client               │
│   HTML5 · CSS3 · JavaScript ES6             │
│   index.html · login.html · place.html      │
└───────────────────┬─────────────────────────┘
                    │ Fetch API (AJAX)
                    ▼
┌─────────────────────────────────────────────┐
│         Part 3 — Flask REST API             │
│   JWT Auth · RBAC · SQLAlchemy · bcrypt     │
│   /api/v1/auth  /places  /reviews  /users   │
└───────────────────┬─────────────────────────┘
                    │ ORM
                    ▼
┌─────────────────────────────────────────────┐
│         SQLite Database                     │
│   users · places · reviews · amenities      │
│   place_amenity (association table)         │
└─────────────────────────────────────────────┘
```

---

## Requirements

```
flask
flask-restx
flask-bcrypt
flask-jwt-extended
flask-sqlalchemy
sqlalchemy
flask-cors
```

Install everything:
```bash
pip install -r part4/hbnb/requirements.txt
```
