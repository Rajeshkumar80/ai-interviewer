/**
 * login.js — AI Interviewer
 * NOTE: Must NOT use type="module" in the <script> tag.
 * Frontend is served by Flask on port 5000 — same origin, no CORS.
 */

// Use relative URL so it works regardless of which port/domain serves the frontend
var BACKEND = (window.location.origin.indexOf("localhost") !== -1 || window.location.origin.indexOf("127.0.0.1") !== -1)
  ? "http://localhost:5000/api"  // local dev
  : "/api";                      // same-origin (Flask serving both)
var DEMO_EMAIL = "demo@aiinterviewer.com";
var DEMO_PASSWORD = "Demo1234!";

// ── GOOGLE SIGN-IN CLIENT ID ──────────────────────────────
// Replace this with your real Client ID from Google Cloud Console
// https://console.cloud.google.com/apis/credentials
var GOOGLE_CLIENT_ID = "301319569638-a3js1ae9pkuov0nuvsaasut2ppd4dq18.apps.googleusercontent.com";

/* ─────────────────────────────────────────────────────────
   Google Identity Services — credential callback
   Called automatically by the GSI library after the user
   selects their Google account.
───────────────────────────────────────────────────────── */
function handleGoogleCredentialResponse(response) {
  // Decode the JWT payload (header.payload.sig — no crypto needed for display)
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
   Wire up the custom Google button once DOM is ready.
   The real g_id_onload div handles One-Tap; this button
   acts as a visible fallback trigger.
───────────────────────────────────────────────────────── */
function initGoogleButton() {
  var btn = document.getElementById("google-signin-btn");
  if (!btn) return;

  // Only initialize if the GSI library loaded and a real Client ID is set
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
    // Library not loaded yet — try again after a short wait
    setTimeout(initGoogleButton, 500);
  }
}


/* ── Utility: show a message to the user ────────────────── */
function showMsg(text, type) {
  var el = document.getElementById("login-message");
  if (!el) { console.error("login-message element not found!"); return; }
  el.textContent = text;
  el.className = type || ""; // "error" | "success" | "info"
  el.style.display = text ? "block" : "none";
}

/* ── Utility: set button loading state ──────────────────── */
function setBtnLoading(btnId, loading, defaultText) {
  var btn = document.getElementById(btnId);
  if (!btn) return;
  btn.disabled = loading;
  btn.textContent = loading ? "Please wait…" : defaultText;
}

/* ── Fetch with manual timeout (no AbortSignal.timeout) ── */
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
    onError("Cannot reach the server. Make sure the backend is running (START.bat), then try again.");
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
  var toggleLogin = document.getElementById("auth-toggle-login");
  var toggleRegister = document.getElementById("auth-toggle-register");
  var fillDemoBtn = document.getElementById("fill-demo-btn");

  /* Make sure message is hidden at start */
  showMsg("", "");

  /* ── Tab switcher ────── */
  if (toggleLogin) {
    toggleLogin.addEventListener("click", function () {
      toggleLogin.classList.add("active");
      toggleLogin.setAttribute("aria-selected", "true");
      if (toggleRegister) { toggleRegister.classList.remove("active"); toggleRegister.setAttribute("aria-selected", "false"); }
      if (loginForm) loginForm.classList.remove("hidden");
      if (registerForm) registerForm.classList.add("hidden");
      showMsg("", "");
    });
  }

  if (toggleRegister) {
    toggleRegister.addEventListener("click", function () {
      toggleRegister.classList.add("active");
      toggleRegister.setAttribute("aria-selected", "true");
      if (toggleLogin) { toggleLogin.classList.remove("active"); toggleLogin.setAttribute("aria-selected", "false"); }
      if (registerForm) registerForm.classList.remove("hidden");
      if (loginForm) loginForm.classList.add("hidden");
      showMsg("", "");
    });
  }

  /* ── Fill demo credentials ────── */
  if (fillDemoBtn) {
    fillDemoBtn.addEventListener("click", function () {
      var emailEl = document.getElementById("login-email");
      var passEl = document.getElementById("login-password");
      if (emailEl) emailEl.value = DEMO_EMAIL;
      if (passEl) passEl.value = DEMO_PASSWORD;
      showMsg("Demo credentials filled. Click Sign In.", "info");
    });
  }

  /* ── LOGIN FORM ────── */
  if (loginForm) {
    console.log("[login.js] login form found, attaching submit handler");

    loginForm.addEventListener("submit", function (e) {
      e.preventDefault();
      console.log("[login.js] login form submitted");

      var email = (document.getElementById("login-email")?.value || "").trim().toLowerCase();
      var password = (document.getElementById("login-password")?.value || "");

      /* Client-side validation */
      if (!email) { showMsg("Please enter your email address.", "error"); return; }
      if (!password) { showMsg("Please enter your password.", "error"); return; }

      showMsg("Signing in…", "info");
      setBtnLoading("login-submit-btn", true, "Sign In →");

      apiLogin(email, password,
        /* success */ function (data) {
          localStorage.removeItem("demo_mode");
          saveSession(data.access_token, data.user);
          showMsg("Login successful! Redirecting…", "success");
          setTimeout(function () { window.location.href = "home.html"; }, 600);
        },
        /* error */ function (errMsg) {
          setBtnLoading("login-submit-btn", false, "Sign In →");
          if (errMsg === "NETWORK") {
            if (email === DEMO_EMAIL && password === DEMO_PASSWORD) {
              showMsg("Backend is offline — logging in as Demo (limited mode).", "info");
              demoOfflineLogin();
              setTimeout(function () { window.location.href = "home.html"; }, 1200);
            } else {
              showMsg(
                "Cannot reach the server. Please run START.bat to start the backend. " +
                "You can also use the demo account: demo@aiinterviewer.com / Demo1234!",
                "error"
              );
            }
          } else {
            showMsg(errMsg, "error");
          }
        }
      );
    });
  } else {
    console.error("[login.js] ERROR: #email-login-form not found in DOM!");
  }

  /* ── REGISTER FORM ────── */
  if (registerForm) {
    console.log("[login.js] register form found, attaching submit handler");

    registerForm.addEventListener("submit", function (e) {
      e.preventDefault();
      console.log("[login.js] register form submitted");

      var name = (document.getElementById("register-name")?.value || "").trim();
      var email = (document.getElementById("register-email")?.value || "").trim().toLowerCase();
      var password = (document.getElementById("register-password")?.value || "");
      var confirm = (document.getElementById("register-password-confirm")?.value || "");

      /* Client-side validation */
      if (!name) { showMsg("Please enter your full name.", "error"); return; }
      if (!email) { showMsg("Please enter your email address.", "error"); return; }
      if (!password) { showMsg("Please enter a password.", "error"); return; }
      if (password.length < 8) { showMsg("Password must be at least 8 characters long.", "error"); return; }
      if (password !== confirm) { showMsg("Passwords do not match. Please re-enter.", "error"); return; }

      showMsg("Creating your account…", "info");
      setBtnLoading("register-submit-btn", true, "Create Account →");

      apiRegister(name, email, password,
        /* success */ function (data) {
          localStorage.removeItem("demo_mode");
          saveSession(data.access_token, data.user);
          showMsg("Account created! Redirecting…", "success");
          setTimeout(function () { window.location.href = "home.html"; }, 600);
        },
        /* error */ function (errMsg) {
          setBtnLoading("register-submit-btn", false, "Create Account →");
          showMsg(errMsg, "error");
        }
      );
    });
  } else {
    console.error("[login.js] ERROR: #register-form not found in DOM!");
  }

}); // end DOMContentLoaded
