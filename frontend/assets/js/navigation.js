/**
 * Shared Navigation — AI Interviewer
 * Handles sidebar, mobile menu, auth guard, logout
 * Theme is FIXED — no switching logic
 */

class Navigation {
  constructor() {
    this.sidebar = document.getElementById('sidebar');
    this.overlay = document.getElementById('sidebar-overlay');
    this.mobileToggle = document.getElementById('mobile-menu-toggle');
    this.navbar = document.getElementById('main-navbar');
    this.currentPage = window.location.pathname.split('/').pop() || 'home.html';
    const API_BASE = "https://ai-interviewer-tv4u.onrender.com";
    this.apiBaseUrl = `${API_BASE}/api`;

    this.init();
  }

  init() {
    this.enforceAuthGuard();
    this.setupMobileMenu();
    this.setActiveNavItem();
    this.setupLogoutButton();
    this.setupScrollEffect();
    this.updateUserAvatar();
  }

  /** Redirect to login if no JWT and page is protected */
  enforceAuthGuard() {
    const publicPages = ['index.html', '', 'feedback.html'];
    if (publicPages.includes(this.currentPage)) return;

    const token = localStorage.getItem('token');
    if (!token) {
      window.location.href = 'index.html';
      return;
    }

    // Show offline-mode banner if using demo without backend
    if (localStorage.getItem('demo_mode') === 'true') {
      this.showOfflineBanner();
    }
  }

  /** Show a subtle top banner when running in offline demo mode */
  showOfflineBanner() {
    if (document.getElementById('offline-mode-banner')) return; // already added
    const banner = document.createElement('div');
    banner.id = 'offline-mode-banner';
    banner.style.cssText = [
      'position:fixed', 'top:68px', 'left:0', 'right:0',
      'background:rgba(183,121,31,0.92)', 'color:#fff',
      'text-align:center', 'font-size:0.80rem', 'font-weight:600',
      'padding:6px 16px', 'z-index:2000', 'letter-spacing:0.02em',
      'backdrop-filter:blur(8px)',
    ].join(';');
    banner.innerHTML =
      '⚠️ Running in offline demo mode — start the backend (START.bat) for full features. ' +
      '<a href="index.html" style="color:#fff;text-decoration:underline;margin-left:8px;">Sign out</a>';
    document.body.insertAdjacentElement('afterbegin', banner);

    // Push main content down so banner doesn't overlap navbar
    const main = document.querySelector('.main-content');
    if (main) main.style.marginTop = (68 + 34) + 'px';
  }

  setupMobileMenu() {
    if (!this.mobileToggle) return;

    this.mobileToggle.addEventListener('click', () => {
      const isVisible = this.sidebar && this.sidebar.classList.contains('visible');
      this.toggleSidebar(!isVisible);
    });

    // Close sidebar when overlay is clicked
    if (this.overlay) {
      this.overlay.addEventListener('click', () => this.toggleSidebar(false));
    }

    // Close sidebar on sidebar link click (mobile)
    document.querySelectorAll('.sidebar-link').forEach(link => {
      link.addEventListener('click', () => {
        if (window.innerWidth < 1025) {
          this.toggleSidebar(false);
        }
      });
    });

    // Handle resize
    window.addEventListener('resize', () => {
      if (window.innerWidth >= 1025) {
        this.toggleSidebar(false);
      }
    });
  }

  toggleSidebar(show) {
    if (!this.sidebar) return;
    if (show) {
      this.sidebar.classList.add('visible');
      if (this.overlay) {
        this.overlay.style.display = 'block';
        requestAnimationFrame(() => this.overlay.classList.add('visible'));
      }
      if (this.mobileToggle) {
        this.mobileToggle.setAttribute('aria-expanded', 'true');
        this.mobileToggle.textContent = '✕';
      }
    } else {
      this.sidebar.classList.remove('visible');
      if (this.overlay) {
        this.overlay.classList.remove('visible');
        setTimeout(() => {
          if (!this.overlay.classList.contains('visible')) {
            this.overlay.style.display = 'none';
          }
        }, 300);
      }
      if (this.mobileToggle) {
        this.mobileToggle.setAttribute('aria-expanded', 'false');
        this.mobileToggle.textContent = '☰';
      }
    }
  }

  setActiveNavItem() {
    const links = document.querySelectorAll('.sidebar-link, .bottom-action-btn, .nav-link');
    links.forEach(link => {
      const href = link.getAttribute('href') || '';
      const isCurrent = href === this.currentPage || href.endsWith('/' + this.currentPage);
      if (isCurrent) {
        link.classList.add('active');
        link.setAttribute('aria-current', 'page');
      } else {
        link.classList.remove('active');
        link.removeAttribute('aria-current');
      }
    });
  }

  setupScrollEffect() {
    if (!this.navbar) return;
    window.addEventListener('scroll', () => {
      if (window.scrollY > 10) {
        this.navbar.classList.add('scrolled');
      } else {
        this.navbar.classList.remove('scrolled');
      }
    }, { passive: true });
  }

  updateUserAvatar() {
    const user = this.getStoredUser();
    if (!user) return;

    const name = encodeURIComponent(user.name || 'User');
    const avatarEls = document.querySelectorAll('#user-avatar, .avatar');
    avatarEls.forEach(img => {
      if (img.tagName === 'IMG') {
        img.src = `https://ui-avatars.com/api/?name=${name}&background=61210F&color=FDF0D5&bold=true`;
        img.alt = user.name || 'User avatar';
        // Make avatar clickable → goes to profile page
        img.style.cursor = 'pointer';
        img.title = 'View Profile';
        img.addEventListener('click', () => {
          window.location.href = 'profile.html';
        });
      }
    });
  }

  getStoredUser() {
    try {
      const raw = localStorage.getItem('user');
      return raw ? JSON.parse(raw) : null;
    } catch { return null; }
  }

  setupLogoutButton() {
    const logoutBtn = document.getElementById('logout-btn');
    if (!logoutBtn) return;

    logoutBtn.addEventListener('click', async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          await fetch(`${this.apiBaseUrl}/auth/logout`, {
            method: 'POST',
            headers: { Authorization: `Bearer ${token}` }
          });
        } catch (e) {
          console.warn('Backend logout failed, clearing token anyway:', e);
        }
      }
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = 'index.html';
    });
  }
}

// Initialize navigation when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => new Navigation());
} else {
  new Navigation();
}
