/*
  HBnB - scripts.js
  Part 4 - Simple Web Client
  Description: Client-side scripts for HBnB application.
               All API interactions, authentication, and DOM updates are handled here.

  API base URL — update this to match your Flask back-end
*/

const API_URL = 'http://localhost:5000/api/v1';

/* ============================================================
   UTILS - Cookie helpers
   ============================================================ */

/**
 * Set a cookie with a given name, value and path
 */
function setCookie(name, value, path = '/') {
  document.cookie = `${name}=${value}; path=${path}`;
}

/**
 * Get a cookie value by name
 * Returns null if the cookie does not exist
 */
function getCookie(name) {
  const match = document.cookie
    .split('; ')
    .find(row => row.startsWith(name + '='));
  return match ? match.split('=')[1] : null;
}

/**
 * Delete a cookie by name
 */
function deleteCookie(name) {
  document.cookie = `${name}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT`;
}

/**
 * Extract a query parameter value from the current URL
 * @param {string} param - The parameter name to extract
 * @returns {string|null} The parameter value or null if not found
 */
function getQueryParam(param) {
  const params = new URLSearchParams(window.location.search);
  return params.get(param);
}

/* ============================================================
   TASK 1 - Login
   ============================================================ */

/**
 * Send login credentials to the API and return the response
 */
async function loginUser(email, password) {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ email, password })
  });
  return response;
}

/**
 * Show an error or success message on the login form
 */
function showLoginMessage(text, type = 'error') {
  const msg = document.getElementById('login-message');
  if (!msg) return;
  msg.textContent = text;
  msg.className = `message ${type}`;
  msg.style.display = 'block';
}

/* ============================================================
   TASK 2 - List of Places
   ============================================================ */

/**
 * Check if the user is authenticated via the JWT cookie.
 * Show/hide the login link accordingly, then fetch places.
 */
function checkAuthentication() {
  const token = getCookie('token');
  const loginLink = document.getElementById('login-link');

  if (loginLink) {
    loginLink.style.display = token ? 'none' : 'block';
  }

  fetchPlaces(token);
}

/**
 * Fetch all places from the API.
 * Sends the JWT token in the Authorization header if available.
 */
async function fetchPlaces(token) {
  try {
    const headers = { 'Content-Type': 'application/json' };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_URL}/places`, { headers });

    if (!response.ok) {
      console.error('Failed to fetch places:', response.statusText);
      return;
    }

    const places = await response.json();

    /* Store places globally for filtering without new requests */
    window._allPlaces = places;

    populatePriceFilter();
    displayPlaces(places);
  } catch (error) {
    console.error('Error fetching places:', error);
  }
}

/**
 * Populate the price filter dropdown with fixed options per task requirements.
 * Options: All, 10, 50, 100
 */
function populatePriceFilter() {
  const select = document.getElementById('price-filter');
  if (!select) return;

  select.innerHTML = '';

  const options = [
    { value: 'all', label: 'All' },
    { value: '10',  label: '10 €' },
    { value: '50',  label: '50 €' },
    { value: '100', label: '100 €' }
  ];

  options.forEach(opt => {
    const option = document.createElement('option');
    option.value = opt.value;
    option.textContent = opt.label;
    select.appendChild(option);
  });
}

/**
 * Create and display place cards in the #places-list container.
 * @param {Array} places - Array of place objects from the API
 */
function displayPlaces(places) {
  const placesList = document.getElementById('places-list');
  if (!placesList) return;

  placesList.innerHTML = '';

  if (places.length === 0) {
    placesList.innerHTML = '<p>No places found for this filter.</p>';
    return;
  }

  places.forEach(place => {
    const card = document.createElement('div');
    card.className = 'place-card';
    card.dataset.price = place.price;

    card.innerHTML = `
      <h3>${place.title}</h3>
      <p class="price">$${place.price} / night</p>
      <a href="place.html?id=${place.id}" class="details-button">View Details</a>
    `;

    placesList.appendChild(card);
  });
}

/* ============================================================
   TASK 3 - Place Details
   ============================================================ */

/**
 * Fetch detailed information for a single place by ID.
 * @param {string} token - JWT token (can be null)
 * @param {string} placeId - The place UUID
 */
async function fetchPlaceDetails(token, placeId) {
  try {
    const headers = { 'Content-Type': 'application/json' };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_URL}/places/${placeId}`, { headers });

    if (!response.ok) {
      document.getElementById('place-details').innerHTML =
        '<p>Place not found or an error occurred.</p>';
      return;
    }

    const place = await response.json();
    displayPlaceDetails(place);

    /* Fetch reviews separately */
    fetchPlaceReviews(token, placeId);
  } catch (error) {
    console.error('Error fetching place details:', error);
  }
}

/**
 * Render the place details section with full info.
 * @param {Object} place - Place object from the API
 */
function displayPlaceDetails(place) {
  const section = document.getElementById('place-details');
  if (!section) return;

  const amenities = place.amenities && place.amenities.length > 0
    ? place.amenities.map(a => `<span class="amenity-tag">${a.name}</span>`).join('')
    : '<span>No amenities listed</span>';

  const owner = place.owner
    ? `${place.owner.first_name} ${place.owner.last_name}`
    : 'Unknown';

  section.innerHTML = `
    <div class="place-details">
      <h1>${place.title}</h1>
      <div class="place-info">
        <div class="info-item">
          <span>Host</span>
          <strong>${owner}</strong>
        </div>
        <div class="info-item">
          <span>Price per night</span>
          <strong>$${place.price}</strong>
        </div>
        <div class="info-item">
          <span>Location</span>
          <strong>${place.latitude.toFixed(4)}, ${place.longitude.toFixed(4)}</strong>
        </div>
      </div>
      <p class="description">${place.description || 'No description available.'}</p>
      <h3>Amenities</h3>
      <div class="amenities-list">${amenities}</div>
    </div>
  `;
}

/**
 * Fetch and display reviews for a place.
 * @param {string} token - JWT token (can be null)
 * @param {string} placeId - The place UUID
 */
async function fetchPlaceReviews(token, placeId) {
  try {
    const headers = { 'Content-Type': 'application/json' };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_URL}/places/${placeId}/reviews`, { headers });

    if (!response.ok) return;

    const reviews = await response.json();
    displayReviews(reviews);
  } catch (error) {
    console.error('Error fetching reviews:', error);
  }
}

/**
 * Render review cards in the #reviews section.
 * @param {Array} reviews - Array of review objects from the API
 */
function displayReviews(reviews) {
  const section = document.getElementById('reviews');
  if (!section) return;

  section.innerHTML = '<h2>Reviews</h2>';

  if (reviews.length === 0) {
    section.innerHTML += '<p>No reviews yet. Be the first to review!</p>';
    return;
  }

  reviews.forEach(review => {
    const stars = '⭐'.repeat(review.rating);
    const card = document.createElement('div');
    card.className = 'review-card';
    card.innerHTML = `
      <p class="reviewer">${review.user_id}</p>
      <p class="rating">${stars} ${review.rating}/5</p>
      <p class="comment">${review.text}</p>
    `;
    section.appendChild(card);
  });
}

/* ============================================================
   TASK 4 - Add Review
   ============================================================ */

/**
 * Submit a review to the API.
 * @param {string} token - JWT token
 * @param {string} placeId - The place UUID
 * @param {string} reviewText - The review content
 * @param {number} rating - Rating from 1 to 5
 */
async function submitReview(token, placeId, reviewText, rating) {
  const response = await fetch(`${API_URL}/reviews`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      text: reviewText,
      rating: parseInt(rating),
      place_id: placeId
    })
  });
  return response;
}

/**
 * Show a message in the review form (success or error)
 */
function showReviewMessage(text, type = 'error') {
  const msg = document.getElementById('review-message');
  if (!msg) return;
  msg.textContent = text;
  msg.className = `message ${type}`;
  msg.style.display = 'block';
}

/* ============================================================
   DOMContentLoaded - Entry point
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

  /* ---------- Task 1 : Login form ---------- */
  const loginForm = document.getElementById('login-form');

  if (loginForm) {
    loginForm.addEventListener('submit', async (event) => {
      event.preventDefault();

      const email    = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value;

      try {
        const response = await loginUser(email, password);

        if (response.ok) {
          const data = await response.json();
          setCookie('token', data.access_token);
          window.location.href = 'index.html';
        } else {
          const err = await response.json().catch(() => null);
          const msg = err?.msg || err?.message || response.statusText || 'Invalid credentials';
          showLoginMessage('Login failed: ' + msg);
        }
      } catch (error) {
        showLoginMessage('An error occurred. Please check your connection and try again.');
        console.error('Login error:', error);
      }
    });
  }

  /* ---------- Task 2 : Index page ---------- */
  const placesList = document.getElementById('places-list');

  if (placesList) {
    checkAuthentication();

    const priceFilter = document.getElementById('price-filter');
    if (priceFilter) {
      priceFilter.addEventListener('change', (event) => {
        const selected = event.target.value;
        const cards = document.querySelectorAll('.place-card');

        cards.forEach(card => {
          const price = parseFloat(card.dataset.price);
          if (selected === 'all' || price <= parseFloat(selected)) {
            card.style.display = 'flex';
          } else {
            card.style.display = 'none';
          }
        });
      });
    }
  }

  /* ---------- Task 3 : Place details page ---------- */
  const placeDetailsSection = document.getElementById('place-details');

  if (placeDetailsSection) {
    const token   = getCookie('token');
    const placeId = getQueryParam('id');

    /* Show/hide the add review section based on authentication */
    const addReviewSection = document.getElementById('add-review');
    if (addReviewSection) {
      addReviewSection.style.display = token ? 'block' : 'none';
    }

    if (placeId) {
      fetchPlaceDetails(token, placeId);
    } else {
      placeDetailsSection.innerHTML = '<p>No place ID provided.</p>';
    }

    /* Review form inside place.html */
    const reviewForm = document.getElementById('review-form');
    if (reviewForm && token && placeId) {
      reviewForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const reviewText = document.getElementById('review-text').value.trim();
        const rating     = document.getElementById('rating').value;

        if (!reviewText || !rating) {
          showReviewMessage('Please fill in all fields.');
          return;
        }

        try {
          const response = await submitReview(token, placeId, reviewText, rating);

          if (response.ok) {
            showReviewMessage('Review submitted successfully!', 'success');
            reviewForm.reset();
            /* Refresh reviews */
            fetchPlaceReviews(token, placeId);
          } else {
            const err = await response.json().catch(() => null);
            const msg = err?.error || err?.message || 'Failed to submit review.';
            showReviewMessage(msg);
          }
        } catch (error) {
          showReviewMessage('An error occurred. Please try again.');
          console.error('Review submission error:', error);
        }
      });
    }
  }

  /* ---------- Task 4 : Add review page (add_review.html) ---------- */
  const addReviewPage = document.getElementById('review-form');
  const isAddReviewPage = window.location.pathname.includes('add_review');

  if (addReviewPage && isAddReviewPage) {
    /* Redirect unauthenticated users to index */
    const token = getCookie('token');
    if (!token) {
      window.location.href = 'index.html';
      return;
    }

    const placeId = getQueryParam('id');

    /* Show place name in title if available */
    if (placeId) {
      fetch(`${API_URL}/places/${placeId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
        .then(r => r.json())
        .then(place => {
          const title = document.getElementById('place-name');
          if (title) title.textContent = `Add a Review — ${place.title}`;
        })
        .catch(() => {});
    }

    addReviewPage.addEventListener('submit', async (event) => {
      event.preventDefault();

      const reviewText = document.getElementById('review').value.trim();
      const rating     = document.getElementById('rating').value;

      if (!reviewText || !rating) {
        showReviewMessage('Please fill in all fields.');
        return;
      }

      try {
        const response = await submitReview(token, placeId, reviewText, rating);

        if (response.ok) {
          showReviewMessage('Review submitted successfully!', 'success');
          addReviewPage.reset();
        } else {
          const err = await response.json().catch(() => null);
          const msg = err?.error || err?.message || 'Failed to submit review.';
          showReviewMessage(msg);
        }
      } catch (error) {
        showReviewMessage('An error occurred. Please try again.');
        console.error('Review submission error:', error);
      }
    });
  }

});
