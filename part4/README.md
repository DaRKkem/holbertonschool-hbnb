# HBnB — Part 4: Simple Web Client

![HTML5](https://img.shields.io/badge/HTML5-semantic-orange)
![CSS3](https://img.shields.io/badge/CSS3-responsive-blue)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow)
![JWT](https://img.shields.io/badge/JWT-cookie--based-orange)
![Fetch API](https://img.shields.io/badge/Fetch-AJAX-lightgrey)
![License](https://img.shields.io/badge/License-Holberton-yellow)

## Overview

Part 4 of the HBnB project adds a **Simple Web Client** on top of the Flask REST API built in Part 3.

It is a fully static front-end (HTML5 / CSS3 / JavaScript ES6) that communicates with the back-end through the Fetch API. No framework, no build tool — plain browser-native code.

Key features:
- **Login** with JWT token stored in a cookie
- **List of places** fetched from the API with client-side price filtering
- **Place details** with owner info, amenities and reviews
- **Add review** form accessible to authenticated users only

---

## Architecture

```
part4/hbnb/
├── index.html          ← List of places (Task 0 + 2)
├── login.html          ← Login form (Task 0 + 1)
├── place.html          ← Place details + inline review form (Task 0 + 3)
├── add_review.html     ← Standalone review form (Task 0 + 4)
├── styles.css          ← Global stylesheet
├── scripts.js          ← All client-side logic
├── images/             ← logo.png, icon.png, place images
└── hbnb/               ← Flask back-end (Part 3, unchanged)
```

---

## Pages

| Page | Description |
|---|---|
| `index.html` | Lists all places fetched from the API. Includes a price filter dropdown. Login button visible only when not authenticated. |
| `login.html` | Email + password form. On success, stores the JWT token in a cookie and redirects to `index.html`. |
| `place.html` | Shows full details of a place (host, price, description, amenities, reviews). Shows the add review form if the user is logged in. |
| `add_review.html` | Standalone review form. Redirects unauthenticated users to `index.html`. |

---

## Project Structure — scripts.js

All client-side logic lives in a single `scripts.js` file, organized by task:

```
scripts.js
├── UTILS          — setCookie(), getCookie(), deleteCookie(), getQueryParam()
├── TASK 1         — loginUser(), showLoginMessage()
├── TASK 2         — checkAuthentication(), fetchPlaces(), displayPlaces(), populatePriceFilter()
├── TASK 3         — fetchPlaceDetails(), displayPlaceDetails(), fetchPlaceReviews(), displayReviews()
├── TASK 4         — submitReview(), showReviewMessage()
└── DOMContentLoaded entry point — routes logic per page
```

---

## Tasks Breakdown

### Task 0 — Design

Complete the HTML/CSS structure for all 4 pages following Holberton design specifications.

**Required classes implemented:**
- `.place-card` — place listing cards
- `.details-button` — "View Details" button
- `.place-details` — place detail wrapper
- `.place-info` — info grid (host, price, location)
- `.review-card` — individual review cards
- `.add-review` — review form section
- `.form` — form styling class
- `.login-button` — login button in header

**Fixed parameters (per spec):**
- Margin: `20px` on place and review cards
- Padding: `10px` inside place and review cards
- Border: `1px solid #ddd`
- Border radius: `10px`

---

### Task 1 — Login

**File:** `login.html` + `scripts.js`

**Flow:**
1. User submits email + password
2. `loginUser()` sends a POST to `/api/v1/auth/login`
3. On success → JWT token stored in cookie (`token=...`) → redirect to `index.html`
4. On failure → error message displayed inline

**How to test:**
```
Email:    admin@hbnb.io
Password: admin1234
```
After login, check the cookie in DevTools → Application → Cookies → `localhost:5500`.

---

### Task 2 — List of Places

**File:** `index.html` + `scripts.js`

**Flow:**
1. On page load, `checkAuthentication()` reads the JWT cookie
2. If no token → Login button shown; if token → Login button hidden
3. `fetchPlaces()` sends GET `/api/v1/places` (with token in header if available)
4. Places are rendered as `.place-card` elements with `data-price` attribute
5. Price filter (All / 10 / 50 / 100) hides/shows cards client-side without reload

**How to test:**
1. Open `index.html` while Flask is running
2. All places should appear
3. Change the price filter → cards are filtered instantly
4. Delete the `token` cookie → Login button reappears

---

### Task 3 — Place Details

**File:** `place.html` + `scripts.js`

**Flow:**
1. Place ID is extracted from the URL: `place.html?id=<uuid>`
2. `fetchPlaceDetails()` sends GET `/api/v1/places/<id>`
3. `displayPlaceDetails()` renders host, price, description, amenities
4. `fetchPlaceReviews()` sends GET `/api/v1/places/<id>/reviews`
5. `displayReviews()` renders review cards
6. Add review form shown only if JWT token is present in cookie

**How to test:**
1. Click "View Details" on any place card
2. Place info, amenities and reviews should load
3. If logged in → review form is visible at the bottom
4. If not logged in → review form is hidden

---

### Task 4 — Add Review

**File:** `add_review.html` + `place.html` + `scripts.js`

**Flow:**
1. On page load, `getCookie('token')` is checked
2. If no token → immediate redirect to `index.html`
3. Place ID is extracted from URL query param
4. `submitReview()` sends POST `/api/v1/reviews/` with token + review data
5. On success → success message + form cleared
6. On failure → error message displayed

**How to test:**
1. Make sure you are logged in
2. Navigate to a place detail page
3. Fill in the review text and rating → Submit
4. The new review should appear in the reviews list
5. Log out (delete the cookie) and try to access `add_review.html?id=<uuid>` directly → you should be redirected to `index.html`

---

## Installation & Running

### Prerequisites

- Python 3.12+
- A modern browser (Chrome, Firefox, Opera GX…)
- VS Code with Live Server extension (recommended)

### 1. Start the Flask back-end

```bash
cd part4/hbnb

# Activate your virtual environment
source /path/to/.venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python3 run.py
```

The API runs on `http://localhost:5000`
Swagger UI: `http://localhost:5000/api/v1/`

### 2. Open the front-end

Open `index.html` with **Live Server** (right-click → Open with Live Server) or any static file server on port 5500.

> The `API_URL` in `scripts.js` is set to `http://localhost:5000/api/v1`. Update it if your Flask server runs on a different port.

### 3. CORS configuration

The Flask app must allow requests from `http://localhost:5500`. In `app/__init__.py`:

```python
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

Also add in `create_app()`:

```python
app.url_map.strict_slashes = False
```

---

## Default Credentials

| Field | Value |
|---|---|
| Admin email | `admin@hbnb.io` |
| Admin password | `admin1234` |

---

## Authentication Flow

```
User fills login form
        │
        ▼
POST /api/v1/auth/login
        │
   response.ok ?
   ┌────┴────┐
  YES        NO
   │          │
setCookie()  showLoginMessage()
   │
redirect → index.html
   │
checkAuthentication() on load
   │
token found ?
   ┌────┴────┐
  YES        NO
   │          │
hide Login  show Login
fetchPlaces()
```

---

## Cookie Management

| Function | Description |
|---|---|
| `setCookie(name, value)` | Stores a value in a browser cookie with `path=/` |
| `getCookie(name)` | Reads a cookie value by name, returns `null` if absent |
| `deleteCookie(name)` | Expires the cookie immediately (logout) |

The JWT token is stored as:
```
token=eyJhbGci...; path=/
```

---

## API Endpoints Used

| Method | Endpoint | Used in |
|---|---|---|
| POST | `/api/v1/auth/login` | Task 1 — Login |
| GET | `/api/v1/places` | Task 2 — List places |
| GET | `/api/v1/places/<id>` | Task 3 — Place details |
| GET | `/api/v1/places/<id>/reviews` | Task 3 — Reviews |
| POST | `/api/v1/reviews` | Task 4 — Submit review |

---

## Authors

- **Sara Rebati**
- **Valentin Planchon**
- **Damien Rossi**

Holberton School — 2026
