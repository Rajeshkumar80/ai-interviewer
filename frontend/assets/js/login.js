/**
 * login.js — AI Interviewer
 * NOTE: Must NOT use type="module" in the <script> tag.
 * Frontend is served by Flask on port 5000 — same origin, no CORS.
 */

// Use absolute URL for Render production deployment
const API_BASE = "https://ai-interviewer-tv4u.onrender.com";
var BACKEND = `${API_BASE}/api`;

var DEMO_EMAIL = "demo@aiinterviewer.com";
var DEMO_PASSWORD = "Demo1234!";

// ── GOOGLE SIGN-IN CLIENT ID ──────────────────────────────
var GOOGLE_CLIENT_ID = "301319569638-a3js1ae9pkuov0nuvsaasut2ppd4dq18.apps.googleusercontent.com";

/* ─────────────────────────────────────────────────────────
   Google Identity Services — credential callback
───────────────────────────────────────────────────────── */
function handleGoogleCredentialResponse(response) {
  var parts = (response.credential || "").split(".");
  var userInfo = {};
  try {
    userInfo = JSON.parse(atob(parts[1].replace(/-/g, "+").replace(/_/g, "/")));
  } catch (e) {
    console.warn("[Google] Could not decode JWT payload:", e);
  }

  showMsg("Signing in with Google…", "info");

  fetch(BACKEND + "/auth/google", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      credential: response.credential,
      user_info: {
        email: userInfo.email || "",
        name: userInfo.name || "",
        picture: userInfo.picture || ""
      }
    })
  })
    .then(function (res) { return res.json(); })
    .then(function (data) {
      if (data.status === "success") {
        localStorage.removeItem("demo_mode");
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("user", JSON.stringify(data.user));
        showMsg("Google sign-in successful! Redirecting…", "success");
        setTimeout(function () { window.location.href = "home.html"; }, 700);
      } else {
        showMsg(data.message || "Google sign-in failed. Please try again.", "error");
      }
    })
    .catch(function (err) {
      console.error("[Google] Login error:", err);
      showMsg("Cannot reach the server. Make sure the backend is running.", "error");
    });
}

/* ─────────────────────────────────────────────────────────
   Wire up the custom Google button
───────────────────────────────────────────────────────── */
function initGoogleButton() {
  var btn = document.getElementById("google-signin-btn");
  if (!btn) return;

  if (GOOGLE_CLIENT_ID === "YOUR_CLIENT_ID") {
    btn.title = "Add your Google Client ID to enable this button.";
    btn.style.opacity = "0.5";
    btn.style.cursor = "not-allowed";
    return;
  }

  if (window.google && window.google.accounts) {
    window.google.accounts.id.initialize({
      client_id: GOOGLE_CLIENT_ID,
      callback: handleGoogleCredentialResponse,
      auto_select: false
    });

    btn.addEventListener("click", function () {
      window.google.accounts.id.prompt();
    });
  } else {
    setTimeout(initGoogleButton, 500);
  }
}

/* ── Utility: show a message to the user ────────────────── */
function showMsg(text, type) {
  var el = document.getElementById("login-message") || document.getElementById("register-message");
  if (!el) { console.error("message element not found!"); return; }
  el.textContent = text;
  el.className = type || "";
  el.style.display = text ? "block" : "none";
}

/* ── Utility: set button loading state ──────────────────── */
function setBtnLoading(btnId, loading, defaultText) {
  var btn = document.getElementById(btnId);
  if (!btn) return;
  btn.disabled = loading;
  btn.textContent = loading ? "Please wait…" : defaultText;
}

/* ── Fetch with manual timeout ───────────────────────────── */
function fetchWithTimeout(url, opts, ms) {
  return new Promise(function (resolve, reject) {
    var timer = setTimeout(function () {
      reject(new Error("TIMEOUT"));
    }, ms || 8000);

    fetch(url, opts).then(function (r) {
      clearTimeout(timer);
      resolve(r);
    }).catch(function (e) {
      clearTimeout(timer);
      reject(e);
    });
  });
}

/* ── Store user in localStorage ─────────────────────────── */
function saveSession(token, user) {
  localStorage.setItem("token", token);
  localStorage.setItem("user", JSON.stringify(user));
}

/* ── Demo offline login ──────────────────────────────────── */
function demoOfflineLogin() {
  localStorage.setItem("demo_mode", "true");
  saveSession("demo_offline_" + Date.now(), {
    id: "demo-offline",
    name: "Demo Candidate",
    email: DEMO_EMAIL,
    picture: ""
  });
}

/* ── API: Login ──────────────────────────────────────────── */
function apiLogin(email, password, onSuccess, onError) {
  fetchWithTimeout(
    BACKEND + "/auth/login",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: email, password: password })
    },
    8000
  ).then(function (res) {
    return res.json().then(function (data) {
      if (!res.ok || data.status !== "success") {
        onError(data.message || "Invalid email or password. Please try again.");
      } else {
        onSuccess(data);
      }
    });
  }).catch(function (err) {
    var msg = err.message || "";
    if (msg === "TIMEOUT" || msg.indexOf("fetch") !== -1 || msg.indexOf("network") !== -1 ||
      msg.indexOf("Failed") !== -1 || msg.indexOf("NetworkError") !== -1) {
      onError("NETWORK");
    } else {
      onError("Could not connect to the server: " + msg);
    }
  });
}

/* ── API: Register ───────────────────────────────────────── */
function apiRegister(name, email, password, onSuccess, onError) {
  fetchWithTimeout(
    BACKEND + "/auth/register",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: name, email: email, password: password })
    },
    8000
  ).then(function (res) {
    return res.json().then(function (data) {
      if (!res.ok || data.status !== "success") {
        onError(data.message || "Registration failed. Please try again.");
      } else {
        onSuccess(data);
      }
    });
  }).catch(function (err) {
    onError("Cannot reach the server. Make sure the backend is running, then try again.");
  });
}

/* ── Main: wire up DOM when page is ready ────────────────── */
document.addEventListener("DOMContentLoaded", function () {

  console.log("[login.js] DOM ready. Wiring up forms…");

  // Initialize Google button
  initGoogleButton();

  /* Redirect if already logged in */
  if (localStorage.getItem("token")) {
    window.location.href = "home.html";
    return;
  }

  var loginForm = document.getElementById("email-login-form");
  var registerForm = document.getElementById("register-form");
  var loginView = document.getElementById("login-view");
  var registerView = document.getElementById("register-view");
  var showRegisterLink = document.getElementById("show-register-link");
  var showLoginLink = document.getElementById("show-login-link");

  /* ── View switcher ────── */
  if (showRegisterLink) {
    showRegisterLink.addEventListener("click", function (e) {
      e.preventDefault();
      if (loginView) loginView.classList.add("hidden");
      if (registerView) registerView.classList.remove("hidden");
    });
  }

  if (showLoginLink) {
    showLoginLink.addEventListener("click", function (e) {
      e.preventDefault();
      if (registerView) registerView.classList.add("hidden");
      if (loginView) loginView.classList.remove("hidden");
    });
  }

  /* ── LOGIN FORM ────── */
  if (loginForm) {
    loginForm.addEventListener("submit", function (e) {
      e.preventDefault();

      var email = (document.getElementById("login-email")?.value || "").trim().toLowerCase();
      var password = (document.getElementById("login-password")?.value || "");

      if (!email) { showMsg("Please enter your email address.", "error"); return; }
      if (!password) { showMsg("Please enter your password.", "error"); return; }

      showMsg("Signing in…", "info");
      setBtnLoading("login-submit-btn", true, "Login");

      apiLogin(email, password,
        function (data) {
          localStorage.removeItem("demo_mode");
          saveSession(data.access_token, data.user);
          showMsg("Login successful! Redirecting…", "success");
          setTimeout(function () { window.location.href = "home.html"; }, 600);
        },
        function (errMsg) {
          setBtnLoading("login-submit-btn", false, "Login");
          if (errMsg === "NETWORK") {
            if (email === DEMO_EMAIL && password === DEMO_PASSWORD) {
              showMsg("Backend is offline — logging in as Demo (limited mode).", "info");
              demoOfflineLogin();
              setTimeout(function () { window.location.href = "home.html"; }, 1200);
            } else {
              showMsg(
                "Cannot reach the server. Please ensure the backend is running.",
                "error"
              );
            }
          } else {
            showMsg(errMsg, "error");
          }
        }
      );
    });
  }

  /* ── REGISTER FORM ────── */
  if (registerForm) {
    registerForm.addEventListener("submit", function (e) {
      e.preventDefault();

      var name = (document.getElementById("register-name")?.value || "").trim();
      var email = (document.getElementById("register-email")?.value || "").trim().toLowerCase();
      var password = (document.getElementById("register-password")?.value || "");
      var confirm = (document.getElementById("register-password-confirm")?.value || "");

      if (!name) { showMsg("Please enter your full name.", "error"); return; }
      if (!email) { showMsg("Please enter your email address.", "error"); return; }
      if (!password) { showMsg("Please enter a password.", "error"); return; }
      if (password.length < 8) { showMsg("Password must be at least 8 characters long.", "error"); return; }
      if (password !== confirm) { showMsg("Passwords do not match.", "error"); return; }

      showMsg("Creating your account…", "info");
      setBtnLoading("register-submit-btn", true, "Create Account");

      apiRegister(name, email, password,
        function (data) {
          localStorage.removeItem("demo_mode");
          saveSession(data.access_token, data.user);
          showMsg("Account created! Redirecting…", "success");
          setTimeout(function () { window.location.href = "home.html"; }, 600);
        },
        function (errMsg) {
          setBtnLoading("register-submit-btn", false, "Create Account");
          showMsg(errMsg, "error");
        }
      );
    });
  }

});
