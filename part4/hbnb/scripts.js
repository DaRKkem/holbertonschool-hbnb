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
    /* Hide login button if already logged in */
    loginLink.style.display = token ? 'none' : 'block';
  }
 
  /* Fetch places regardless — API is public for listing */
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
 
  /* Clear current content */
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
          /* Login successful — store JWT token in cookie and redirect */
          const data = await response.json();
          setCookie('token', data.access_token);
          window.location.href = 'index.html';
        } else {
          /* Login failed — display error message */
          const err = await response.json().catch(() => null);
          const msg = err?.msg || err?.message || response.statusText || 'Invalid credentials';
          showLoginMessage('Login failed: ' + msg);
        }
      } catch (error) {
        /* Network or unexpected error */
        showLoginMessage('An error occurred. Please check your connection and try again.');
        console.error('Login error:', error);
      }
    });
  }
 
  /* ---------- Task 2 : Index page ---------- */
  const placesList = document.getElementById('places-list');
 
  if (placesList) {
    /* Check auth and load places on index.html */
    checkAuthentication();
 
    /* Price filter — client-side filtering, no page reload */
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
 
});
