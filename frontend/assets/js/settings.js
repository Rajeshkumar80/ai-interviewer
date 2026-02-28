/**
 * Settings Page — AI Interviewer
 * Handles audio settings, notifications, export (CSV + PDF), account actions
 * Theme is FIXED — no theme/dark-mode switching
 */

class SettingsManager {
  constructor() {
    const API_BASE = "https://ai-interviewer-tv4u.onrender.com";
    this.apiBaseUrl = `${API_BASE}/api`;
    this.analyticsData = null;
    this.init();
  }

  async init() {
    this.setupEventListeners();
    this.loadSettings();
    await this.fetchAnalyticsData();
  }

  setupEventListeners() {
    // Volume slider
    const volumeSlider = document.getElementById('playback-volume');
    if (volumeSlider) {
      volumeSlider.addEventListener('input', e => {
        const volumeValue = document.getElementById('volume-value');
        if (volumeValue) volumeValue.textContent = e.target.value + '%';
        localStorage.setItem('playbackVolume', e.target.value);
      });
    }

    // Export buttons
    document.getElementById('export-csv-btn')?.addEventListener('click', () => this.exportData('csv'));
    document.getElementById('export-pdf-btn')?.addEventListener('click', () => this.exportData('pdf'));

    // Delete account
    document.getElementById('delete-account-btn')?.addEventListener('click', () => this.deleteAccount());

    // Logout
    document.getElementById('logout-btn')?.addEventListener('click', () => this.logout());

    // Notification toggles — persist to localStorage
    ['email-notifications', 'reminder-notifications', 'autoplay-toggle'].forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        el.addEventListener('change', () => localStorage.setItem(id, el.checked));
      }
    });
  }

  loadSettings() {
    // Volume
    const savedVolume = localStorage.getItem('playbackVolume') || '75';
    const volumeSlider = document.getElementById('playback-volume');
    if (volumeSlider) {
      volumeSlider.value = savedVolume;
      const volumeValue = document.getElementById('volume-value');
      if (volumeValue) volumeValue.textContent = savedVolume + '%';
    }

    // Toggle states
    ['email-notifications', 'reminder-notifications', 'autoplay-toggle'].forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        const saved = localStorage.getItem(id);
        if (saved !== null) el.checked = saved === 'true';
      }
    });
  }

  /** Fetch analytics data for export */
  async fetchAnalyticsData() {
    try {
      const token = localStorage.getItem('token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};

      const [overviewRes, attemptsRes] = await Promise.all([
        fetch(`${this.apiBaseUrl}/analytics/overview`, { headers }),
        fetch(`${this.apiBaseUrl}/analytics/attempts`, { headers })
      ]);

      const overviewJson = overviewRes.ok ? await overviewRes.json() : {};
      const attemptsJson = attemptsRes.ok ? await attemptsRes.json() : {};

      this.analyticsData = {
        overview: overviewJson.overview || {},
        attempts: attemptsJson.attempts || []
      };
    } catch (e) {
      console.warn('Could not fetch analytics data for export:', e);
      this.analyticsData = { overview: {}, attempts: [] };
    }
  }

  async exportData(format) {
    // Ensure data is loaded
    if (!this.analyticsData) {
      await this.fetchAnalyticsData();
    }

    const btn = document.getElementById(`export-${format}-btn`);
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<span>⏳</span><span>Exporting...</span>`;
    }

    try {
      if (format === 'csv') {
        this.downloadCSV();
      } else if (format === 'pdf') {
        this.downloadPDF();
      }
    } catch (err) {
      console.error('Export error:', err);
      alert('Export failed. Please try again.');
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = format === 'csv'
          ? '<span>📊</span><span>Export CSV</span>'
          : '<span>📄</span><span>Export PDF</span>';
      }
    }
  }

  downloadCSV() {
    const { overview, attempts } = this.analyticsData;
    const now = new Date().toISOString().split('T')[0];
    const user = this.getStoredUser();
    const userName = user?.name || 'User';

    let csv = '';

    // Summary section
    csv += '## AI Interviewer — Analytics Export\n';
    csv += `## Generated: ${new Date().toLocaleString()}\n`;
    csv += `## User: ${userName}\n\n`;

    csv += '### SUMMARY\n';
    csv += 'Metric,Value\n';
    csv += `Total Attempts,${overview.totalAttempts || 0}\n`;
    csv += `Average Score,${Math.round(overview.avgScore || 0)}%\n`;
    csv += `Total Practice Time (hours),${(overview.totalTimeHours || 0).toFixed(1)}\n\n`;

    // Attempt history
    csv += '### ATTEMPT HISTORY\n';
    csv += 'ID,Title,Date,Score (%),Time Taken (s),Correct,Total\n';

    if (attempts.length === 0) {
      csv += 'No attempts recorded yet.\n';
    } else {
      attempts.forEach(a => {
        const title = `"${(a.title || 'Interview').replace(/"/g, '""')}"`;
        const date = a.date || a.started_at ? new Date(a.date || a.started_at).toLocaleDateString() : '—';
        const score = Math.round(a.score || 0);
        const time = Math.round(a.time_taken || 0);
        const correct = a.correct || 0;
        const total = a.total || 0;
        csv += `${a.id || ''},${title},${date},${score},${time},${correct},${total}\n`;
      });
    }

    // Topic performance
    if (overview.topicPerformance && overview.topicPerformance.length > 0) {
      csv += '\n### TOPIC PERFORMANCE\n';
      csv += 'Topic,Average Score (%)\n';
      overview.topicPerformance.forEach(t => {
        csv += `"${t.topic}",${Math.round(t.score || 0)}\n`;
      });
    }

    // Difficulty breakdown
    if (overview.difficultyBreakdown) {
      const d = overview.difficultyBreakdown;
      csv += '\n### DIFFICULTY BREAKDOWN\n';
      csv += 'Difficulty,Correct,Total,Accuracy (%)\n';
      ['easy', 'medium', 'hard'].forEach(level => {
        const obj = d[level] || { correct: 0, total: 0 };
        const acc = obj.total ? Math.round((obj.correct / obj.total) * 100) : 0;
        csv += `${level.charAt(0).toUpperCase() + level.slice(1)},${obj.correct},${obj.total},${acc}\n`;
      });
    }

    this.triggerDownload(csv, `ai-interviewer-report-${now}.csv`, 'text/csv;charset=utf-8;');
  }

  downloadPDF() {
    const { overview, attempts } = this.analyticsData;
    const now = new Date().toLocaleString();
    const user = this.getStoredUser();
    const userName = user?.name || 'User';

    const styles = `
      body { font-family: Arial, sans-serif; color: #2A140E; background: #FDF0D5; margin: 0; padding: 24px; }
      .header { background: linear-gradient(135deg,#61210F,#8B3A22); color: white; padding: 30px; border-radius: 12px; margin-bottom: 24px; }
      .header h1 { margin: 0 0 6px; font-size: 24px; }
      .header p  { margin: 0; opacity: 0.85; font-size: 14px; }
      .section   { background: rgba(255,255,255,0.75); border: 1px solid rgba(97,33,15,0.15); border-radius: 10px; padding: 20px; margin-bottom: 20px; }
      .section h2 { margin: 0 0 16px; font-size: 16px; color: #61210F; border-bottom: 2px solid rgba(97,33,15,0.15); padding-bottom: 8px; }
      .stats-row { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 16px; }
      .stat-box  { flex: 1; min-width: 120px; background: rgba(97,33,15,0.06); border-radius: 8px; padding: 14px; text-align: center; }
      .stat-box .value { font-size: 28px; font-weight: bold; color: #61210F; }
      .stat-box .label { font-size: 12px; color: #6B3A2A; margin-top: 4px; }
      table { width: 100%; border-collapse: collapse; font-size: 13px; }
      th { background: rgba(97,33,15,0.10); color: #2A140E; padding: 10px 8px; text-align: left; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
      td { padding: 9px 8px; border-bottom: 1px solid rgba(97,33,15,0.10); }
      tr:nth-child(even) td { background: rgba(97,33,15,0.03); }
      .badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
      .badge.good { background: rgba(45,106,79,0.12); color: #2D6A4F; }
      .badge.mid  { background: rgba(183,121,31,0.12); color: #B7791F; }
      .badge.low  { background: rgba(192,57,43,0.12);  color: #C0392B; }
      .footer { text-align: center; font-size: 11px; color: #9B6B5A; margin-top: 24px; }
    `;

    const getScoreClass = s => s >= 80 ? 'good' : s >= 60 ? 'mid' : 'low';

    const attemptsHTML = attempts.length === 0
      ? '<p style="color:#9B6B5A;font-size:13px;">No attempts recorded yet.</p>'
      : `<table>
          <thead><tr><th>#</th><th>Title</th><th>Date</th><th>Score</th><th>Duration</th></tr></thead>
          <tbody>
            ${attempts.map((a, i) => {
        const score = Math.round(a.score || 0);
        const date = a.date || a.started_at ? new Date(a.date || a.started_at).toLocaleDateString() : '—';
        const mins = Math.round((a.time_taken || 0) / 60);
        return `<tr>
                <td>${i + 1}</td>
                <td>${this.escapeHtml(a.title || 'Interview')}</td>
                <td>${date}</td>
                <td><span class="badge ${getScoreClass(score)}">${score}%</span></td>
                <td>${mins} min</td>
              </tr>`;
      }).join('')}
          </tbody>
        </table>`;

    const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>AI Interviewer — Performance Report</title>
<style>${styles}</style>
</head>
<body>
  <div class="header">
    <h1>🎯 AI Interviewer — Performance Report</h1>
    <p>Generated: ${now} &nbsp;|&nbsp; User: ${this.escapeHtml(userName)}</p>
  </div>

  <div class="section">
    <h2>📊 Summary Statistics</h2>
    <div class="stats-row">
      <div class="stat-box">
        <div class="value">${overview.totalAttempts || 0}</div>
        <div class="label">Total Attempts</div>
      </div>
      <div class="stat-box">
        <div class="value">${Math.round(overview.avgScore || 0)}%</div>
        <div class="label">Average Score</div>
      </div>
      <div class="stat-box">
        <div class="value">${(overview.totalTimeHours || 0).toFixed(1)}h</div>
        <div class="label">Time Practiced</div>
      </div>
    </div>
  </div>

  <div class="section">
    <h2>📋 Attempt History</h2>
    ${attemptsHTML}
  </div>

  ${overview.topicPerformance && overview.topicPerformance.length > 0 ? `
  <div class="section">
    <h2>📚 Topic Performance</h2>
    <table>
      <thead><tr><th>Topic</th><th>Score</th></tr></thead>
      <tbody>
        ${overview.topicPerformance.map(t => {
      const s = Math.round(t.score || 0);
      return `<tr><td>${this.escapeHtml(t.topic)}</td><td><span class="badge ${getScoreClass(s)}">${s}%</span></td></tr>`;
    }).join('')}
      </tbody>
    </table>
  </div>` : ''}

  <div class="footer">
    AI Interviewer Platform — Confidential Report &nbsp;|&nbsp; ${new Date().getFullYear()}
  </div>
</body>
</html>`;

    // Use an invisible iframe to trigger the print dialog. 
    // This entirely avoids popup blockers, which often block window.open after async fetch calls.
    const iframe = document.createElement('iframe');
    iframe.style.display = 'none';
    document.body.appendChild(iframe);

    iframe.contentDocument.write(html);
    iframe.contentDocument.close();

    // Wait a brief moment for styles to apply before triggering print
    setTimeout(() => {
      try {
        iframe.contentWindow.focus();
        iframe.contentWindow.print();
      } catch (e) {
        console.error('Print failed:', e);
      }

      // Clean up the iframe after the print dialog closes (or immediately if cancelled)
      setTimeout(() => {
        if (document.body.contains(iframe)) {
          document.body.removeChild(iframe);
        }
      }, 5000);
    }, 500);
  }

  triggerDownload(content, filename, mimeType) {
    const BOM = '\uFEFF'; // UTF-8 BOM for proper Excel rendering
    const blob = new Blob([BOM + content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  getStoredUser() {
    try {
      const raw = localStorage.getItem('user');
      return raw ? JSON.parse(raw) : null;
    } catch { return null; }
  }

  deleteAccount() {
    if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      if (confirm('This will permanently delete all your data and progress. Are you absolutely sure?')) {
        alert('Account deletion is disabled in the demo environment. Please contact support.');
      }
    }
  }

  logout() {
    if (confirm('Are you sure you want to sign out?')) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = 'index.html';
    }
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => new SettingsManager());
} else {
  new SettingsManager();
}
