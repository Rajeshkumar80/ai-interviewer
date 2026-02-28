/**
 * Home Page JavaScript
 * Handles stats loading, animations, and interactions
 */

class HomePage {
  constructor() {
    this.apiBaseUrl = 'http://localhost:5000/api';
    this.init();
  }

  async init() {
    this.setupEventListeners();
    await this.loadUserStats();
    this.setupAnimations();
  }

  setupEventListeners() {
    // Help bubble
    const helpBubble = document.getElementById('help-bubble');
    if (helpBubble) {
      helpBubble.addEventListener('click', () => this.showHelp());
    }

    // Intersection Observer for animations
    this.setupScrollAnimations();
  }

  async loadUserStats() {
    try {
      // In a real app, this would fetch from the API
      // For now, we'll use mock data
      const stats = {
        totalInterviews: 12,
        avgScore: 78,
        streakDays: 5,
        topicsMastered: 8
      };

      // Animate numbers
      this.animateValue('total-interviews', 0, stats.totalInterviews, 1000);
      this.animateValue('avg-score', 0, stats.avgScore, 1000, '%');
      this.animateValue('streak-days', 0, stats.streakDays, 1000);
      this.animateValue('topics-mastered', 0, stats.topicsMastered, 1000);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  }

  animateValue(id, start, end, duration, suffix = '') {
    const element = document.getElementById(id);
    if (!element) return;

    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
      current += increment;
      if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
        current = end;
        clearInterval(timer);
      }
      element.textContent = Math.floor(current) + suffix;
    }, 16);
  }

  setupAnimations() {
    // Stagger animation for feature cards
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach((card, index) => {
      card.style.animationDelay = `${index * 0.1}s`;
    });

    // Parallax effect for hero section
    window.addEventListener('scroll', () => {
      const scrolled = window.pageYOffset;
      const heroVisual = document.querySelector('.hero-visual');
      if (heroVisual) {
        heroVisual.style.transform = `translateY(${scrolled * 0.1}px)`;
      }
    });
  }

  setupScrollAnimations() {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-fade-in');
          observer.unobserve(entry.target);
        }
      });
    }, observerOptions);

    // Observe all cards
    document.querySelectorAll('.card').forEach(card => {
      observer.observe(card);
    });
  }

  showHelp() {
    // Show help modal or tooltip
    alert('Welcome to AI Interviewer! Click on any section in the sidebar to get started. Use the theme toggle to customize your experience.');
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => new HomePage());
} else {
  new HomePage();
}
