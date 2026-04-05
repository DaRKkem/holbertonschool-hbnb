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

});
