/**
 * Profile Page JavaScript
 * Handles profile form, avatar upload, and profile management
 */

class ProfileManager {
  constructor() {
    const API_BASE = "https://ai-interviewer-tv4u.onrender.com";
    this.apiBaseUrl = `${API_BASE}/api`;
    this.init();
  }

  async init() {
    this.setupEventListeners();
    await this.loadProfile();
  }

  setupEventListeners() {
    // Avatar upload
    const avatarEditBtn = document.getElementById('avatar-edit-btn');
    const avatarUpload = document.getElementById('avatar-upload');

    if (avatarEditBtn && avatarUpload) {
      avatarEditBtn.addEventListener('click', () => avatarUpload.click());
      avatarUpload.addEventListener('change', (e) => this.handleAvatarUpload(e));
    }

    // Tag inputs
    this.setupTagInput('languages-input', 'languages-tags');
    this.setupTagInput('target-roles-input', 'target-roles-tags');

    // Form submission
    const profileForm = document.getElementById('profile-form');
    if (profileForm) {
      profileForm.addEventListener('submit', (e) => this.handleFormSubmit(e));
    }

    // Cancel button
    const cancelBtn = document.getElementById('cancel-btn');
    if (cancelBtn) {
      cancelBtn.addEventListener('click', () => this.loadProfile());
    }
  }

  setupTagInput(inputId, containerId) {
    const input = document.getElementById(inputId);
    const container = document.getElementById(containerId);

    if (!input || !container) return;

    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && input.value.trim()) {
        e.preventDefault();
        this.addTag(input.value.trim(), container);
        input.value = '';
      }
    });
  }

  addTag(text, container) {
    const tag = document.createElement('div');
    tag.className = 'tag';
    tag.innerHTML = `
      <span>${text}</span>
      <span class="tag-remove" data-tag="${text}">×</span>
    `;

    tag.querySelector('.tag-remove').addEventListener('click', () => tag.remove());
    container.appendChild(tag);
  }

  getTags(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return [];
    return Array.from(container.querySelectorAll('.tag span:first-child')).map(tag => tag.textContent);
  }

  async loadProfile() {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        window.location.href = 'index.html';
        return;
      }

      const res = await fetch(`${this.apiBaseUrl}/profile`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await res.json();
      if (!res.ok || data.status !== 'success') {
        console.error('Failed to load profile:', data);
        return;
      }

      const profile = data.profile || {};
      const stats = data.stats || {};

      const fullName = profile.name || profile.full_name || 'User';
      const email = profile.email || '';
      const phone = profile.phone || '';
      const location = profile.location || '';
      const role = profile.role || 'Software Engineer';
      const experience = profile.experience || '';
      const primaryLanguages = profile.primary_languages || [];
      const targetRoles = profile.target_roles || [];

      const avgScore = typeof stats.average_score === 'number' ? Math.round(stats.average_score) : null;
      const totalInterviews = typeof stats.total_interviews === 'number' ? stats.total_interviews : 0;

      const fullNameInput = document.getElementById('full-name');
      if (fullNameInput) fullNameInput.value = fullName;
      const emailInput = document.getElementById('email');
      if (emailInput) emailInput.value = email;
      const phoneInput = document.getElementById('phone');
      if (phoneInput) phoneInput.value = phone;
      const locationInput = document.getElementById('location');
      if (locationInput) locationInput.value = location;
      const roleInput = document.getElementById('role');
      if (roleInput) roleInput.value = role;
      const expInput = document.getElementById('experience');
      if (expInput) expInput.value = experience;
      const githubInput = document.getElementById('github');
      if (githubInput) githubInput.value = github;
      const linkedinInput = document.getElementById('linkedin');
      if (linkedinInput) linkedinInput.value = linkedin;
      const tzInput = document.getElementById('timezone');
      if (tzInput) tzInput.value = timezone;

      const languagesContainer = document.getElementById('languages-tags');
      if (languagesContainer) {
        languagesContainer.innerHTML = '';
        primaryLanguages.forEach(lang => this.addTag(lang, languagesContainer));
      }

      const targetRolesContainer = document.getElementById('target-roles-tags');
      if (targetRolesContainer) {
        targetRolesContainer.innerHTML = '';
        targetRoles.forEach(r => this.addTag(r, targetRolesContainer));
      }

      const avatarEl = document.getElementById('profile-avatar');
      if (avatarEl && profile.picture) {
        avatarEl.src = profile.picture;
      }

      const nameEl = document.getElementById('profile-name');
      if (nameEl) nameEl.textContent = fullName;
      const roleEl = document.getElementById('profile-role');
      if (roleEl) roleEl.textContent = role;
      const scoreEl = document.getElementById('profile-score');
      if (scoreEl) scoreEl.textContent = avgScore != null ? `${avgScore}%` : '—';
      const interviewsEl = document.getElementById('profile-interviews');
      if (interviewsEl) interviewsEl.textContent = totalInterviews;
    } catch (error) {
      console.error('Error loading profile:', error);
    }
  }

  async handleAvatarUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      alert('Please select an image file');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      alert('Image size should be less than 5MB');
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      const avatar = document.getElementById('profile-avatar');
      if (avatar) {
        avatar.src = event.target.result;
      }
    };
    reader.readAsDataURL(file);

    // In production, upload to server
    // await this.uploadAvatar(file);
  }

  async handleFormSubmit(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const profileData = {
      name: formData.get('full_name'),
      email: formData.get('email'),
      phone: formData.get('phone'),
      location: formData.get('location'),
      role: formData.get('role'),
      experience: formData.get('experience'),
      primary_languages: this.getTags('languages-tags'),
      target_roles: this.getTags('target-roles-tags')
    };

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        window.location.href = 'index.html';
        return;
      }

      const response = await fetch(`${this.apiBaseUrl}/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(profileData)
      });

      const data = await response.json();
      if (!response.ok || data.status !== 'success') {
        throw new Error(data.message || 'Failed to save profile');
      }

      alert('Profile saved successfully!');
      await this.loadProfile();
    } catch (error) {
      console.error('Error saving profile:', error);
      alert('Failed to save profile. Please try again.');
    }
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => new ProfileManager());
} else {
  new ProfileManager();
}

