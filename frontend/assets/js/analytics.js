class AnalyticsManager {
  constructor() {
    const API_BASE = "https://ai-interviewer-tv4u.onrender.com";
    this.apiBaseUrl = `${API_BASE}/api/analytics`;
    this.charts = {};
    this.init();
  }

  async init() {
    await this.loadAnalyticsData();
    this.initializeCharts();
    this.renderHeatmap();
    this.renderAttemptHistory();
    this.renderStrengthsAndWeaknesses();
    this.renderLearningPlan();
  }

  async loadAnalyticsData() {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const headers = { 'Authorization': `Bearer ${token}` };

      // Overview: aggregate stats & charts
      const overviewRes = await fetch(
        this.apiBaseUrl.replace("/analytics", "/analytics/overview"),
        { headers }
      );
      const overviewJson = await overviewRes.json();
      const overview = overviewJson.overview || {};

      const totalAttempts = overview.totalAttempts || 0;
      const avgScore = overview.avgScore || 0;
      const totalTimeHours = overview.totalTimeHours || 0; // already in hours from backend
      const scoreTrend = overview.scoreTrend || [];
      const topicPerformance = overview.topicPerformance || [];
      const timePerQuestion = overview.timePerQuestion || [];
      const difficultyBreakdown =
        overview.difficultyBreakdown || {
          easy: { correct: 0, total: 0 },
          medium: { correct: 0, total: 0 },
          hard: { correct: 0, total: 0 },
        };
      const strengths = overview.strengths || [];
      const weaknesses = overview.weaknesses || [];

      // Recent attempts list
      const attemptsRes = await fetch(`${this.apiBaseUrl}/attempts`, { headers });
      const attemptsData = await attemptsRes.json();
      const attemptsList = attemptsData.attempts || [];

      // Weak areas / personalized learning plan
      const weakAreasRes = await fetch(`${this.apiBaseUrl}/weak-areas`, { headers });
      const weakAreasData = await weakAreasRes.json();
      const weakAreas = weakAreasData.weak_areas || [];

      this.data = {
        attempts: attemptsList,
        scoreTrend,
        totalAttempts,
        avgScore,
        totalTime: totalTimeHours,
        topicPerformance,
        timePerQuestion,
        difficultyBreakdown,
        strengths,
        weaknesses,
        weakAreas,
      };

      this.animateValue("total-attempts", 0, this.data.totalAttempts, 800);
      this.animateValue("avg-score", 0, this.data.avgScore, 800, "%");
      const totalTimeEl = document.getElementById("total-time");
      if (totalTimeEl) {
        totalTimeEl.textContent = `${this.data.totalTime.toFixed(1)}h`;
      }
    } catch (e) {
      console.error("Analytics error:", e);
    }
  }

  animateValue(id, start, end, duration, suffix = "") {
    const el = document.getElementById(id);
    if (!el) return;
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
      current += increment;
      if (current >= end) {
        current = end;
        clearInterval(timer);
      }
      el.textContent = Math.floor(current) + suffix;
    }, 16);
  }

  generateTopicPerformance(attempts) {
    const topics = {};
    attempts.forEach((a) => {
      (a.topics || []).forEach((t) => {
        if (!topics[t]) topics[t] = [];
        topics[t].push(a.score);
      });
    });
    return Object.keys(topics).map((t) => ({
      topic: t,
      score:
        topics[t].reduce((s, v) => s + v, 0) / topics[t].length || 0,
    }));
  }

  generateTimePerQuestion(attempts) {
    let result = [];
    attempts.forEach((a) => {
      if (a.question_times) result.push(...a.question_times);
    });
    return result;
  }

  generateDifficulty(attempts) {
    const diff = {
      easy: { correct: 0, total: 0 },
      medium: { correct: 0, total: 0 },
      hard: { correct: 0, total: 0 },
    };

    attempts.forEach((a) => {
      const d = a.difficulty || "medium";
      diff[d].correct += a.correct || 0;
      diff[d].total += a.total || 1;
    });

    return diff;
  }

  collectStrengths(attempts) {
    const list = [];
    attempts.forEach((a) => {
      if (a.strengths) list.push(...a.strengths);
    });
    return list;
  }

  collectWeaknesses(attempts) {
    const list = [];
    attempts.forEach((a) => {
      if (a.weaknesses) list.push(...a.weaknesses);
    });
    return list;
  }

  initializeCharts() {
    this.scoreTrendChart();
    this.topicPerformanceChart();
    this.timeChart();
    this.difficultyChart();
  }

  scoreTrendChart() {
    const ctx = document.getElementById("score-trend-chart");
    if (!ctx) return;

    new Chart(ctx, {
      type: "line",
      data: {
        labels: this.data.scoreTrend.map((d) =>
          new Date(d.date).toLocaleDateString()
        ),
        datasets: [
          {
            label: "Score",
            data: this.data.scoreTrend.map((d) => d.score),
            borderColor: "rgb(99, 102, 241)",
            fill: true,
          },
        ],
      },
    });
  }

  topicPerformanceChart() {
    const ctx = document.getElementById("topic-performance-chart");
    if (!ctx) return;

    new Chart(ctx, {
      type: "bar",
      data: {
        labels: this.data.topicPerformance.map((t) => t.topic),
        datasets: [
          {
            label: "Score",
            data: this.data.topicPerformance.map((t) => t.score),
            backgroundColor: "rgba(99, 102, 241, 0.7)",
          },
        ],
      },
    });
  }

  timeChart() {
    const ctx = document.getElementById("time-per-question-chart");
    if (!ctx) return;

    new Chart(ctx, {
      type: "bar",
      data: {
        labels: this.data.timePerQuestion.map((_, i) => `Q${i + 1}`),
        datasets: [
          {
            data: this.data.timePerQuestion,
            backgroundColor: "rgba(16, 185, 129, 0.7)",
          },
        ],
      },
    });
  }

  difficultyChart() {
    const ctx = document.getElementById("difficulty-chart");
    if (!ctx) return;

    const d = this.data.difficultyBreakdown;
    const pct = (obj) => (obj && obj.total ? (obj.correct / obj.total) * 100 : 0);
    const values = [
      pct(d.easy || {}),
      pct(d.medium || {}),
      pct(d.hard || {}),
    ];

    new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: ["Easy", "Medium", "Hard"],
        datasets: [
          {
            data: values,
            backgroundColor: [
              "rgba(16,185,129,0.7)",
              "rgba(245,158,11,0.7)",
              "rgba(239,68,68,0.7)",
            ],
          },
        ],
      },
    });
  }

  renderHeatmap() {
    const container = document.getElementById("performance-heatmap");
    if (!container) return;

    container.innerHTML = this.data.attempts
      .map((a) => {
        const score = a.score || 0;
        let cls =
          score >= 80
            ? "excellent"
            : score >= 60
              ? "good"
              : score >= 40
                ? "average"
                : "poor";

        return `<div class="heatmap-cell ${cls}">${score}</div>`;
      })
      .join("");
  }

  renderAttemptHistory() {
    const container = document.getElementById("attempt-history");
    if (!container) return;

    if (!this.data.attempts || this.data.attempts.length === 0) {
      container.innerHTML = '<p class="text-muted">No attempts yet.</p>';
      return;
    }

    container.innerHTML = this.data.attempts
      .map(
        (a) => `
      <div class="attempt-item" data-session-id="${a.id}" style="cursor: pointer;">
        <div class="attempt-info">
          <div class="attempt-title">${a.title || "Interview"}</div>
          <div class="attempt-meta">${a.date}</div>
        </div>
        <div class="attempt-score">${a.score}%</div>
        <button class="btn-sm btn-outline-primary" style="margin-left: 10px;">View</button>
      </div>
    `
      )
      .join("");

    // Add click listeners
    container.querySelectorAll(".attempt-item").forEach(item => {
      item.addEventListener("click", () => {
        const sessionId = item.getAttribute("data-session-id");
        if (sessionId) this.showAttemptDetails(sessionId);
      });
    });
  }

  async showAttemptDetails(sessionId) {
    try {
      const token = localStorage.getItem('token');
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
      const res = await fetch(`${this.apiBaseUrl.replace('/analytics', '/interview')}/${sessionId}/results`, { headers });
      if (!res.ok) throw new Error("Failed to load details");
      const data = await res.json();
      const answers = data.answers || [];
      const completedAt = data.completed_at || data.started_at || null;
      const dateLabel = completedAt
        ? new Date(completedAt).toLocaleDateString()
        : new Date().toLocaleDateString();

      // Simple modal implementation
      let modalOverlay = document.getElementById("detail-modal");
      if (!modalOverlay) {
        modalOverlay = document.createElement("div");
        modalOverlay.id = "detail-modal";
        modalOverlay.className = "modal-overlay";
        // Add basic styles dynamically if css not present
        modalOverlay.style.cssText = "position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);display:flex;justify-content:center;align-items:center;z-index:1000;";
        document.body.appendChild(modalOverlay);
      }

      const contentHtml = `
        <div class="modal-content" style="background:var(--bg-card, #fff);padding:20px;border-radius:12px;width:90%;max-width:800px;max-height:90vh;overflow-y:auto;position:relative;color:var(--text-primary, #333);">
           <button id="close-modal-btn" style="position:absolute;top:15px;right:15px;border:none;background:none;font-size:24px;cursor:pointer;">&times;</button>
           <h2>${data.role || "Interview Details"}</h2>
           <div style="margin-bottom:15px;display:flex;gap:15px;font-size:0.9em;color:var(--text-secondary, #666);">
             <span>Date: ${dateLabel}</span>
             <span>Score: ${data.score}%</span>
             <span>Time: ${Math.round(data.time_taken || 0)}s</span>
           </div>
           <div class="modal-questions">
             ${answers.map((ans, idx) => {
        const isCorrect = (ans.evaluation && (ans.evaluation.is_correct || ans.evaluation.passed)) || (ans.evaluation && ans.evaluation.score >= 50);
        return `
                 <div style="border:1px solid var(--border-color, #eee);border-radius:8px;padding:15px;margin-bottom:10px;background:var(--bg-main, #f9fafb);">
                   <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
                     <strong>Q${idx + 1}: ${this.escapeHtml(ans.question)}</strong>
                     <span style="color:${isCorrect ? 'green' : 'red'}">${isCorrect ? 'Correct' : 'Incorrect'}</span>
                   </div>
                   <div style="font-size:0.9em;white-space:pre-wrap;background:var(--bg-card, #fff);padding:10px;border-radius:4px;">${this.escapeHtml(ans.answer_text || "No answer")}</div>
                   <div style="margin-top:8px;font-size:0.85em;color:var(--text-secondary, #555);">
                     <em>Reference: ${this.escapeHtml(ans.evaluation?.reference_answer || ans.evaluation?.solution_explanation || "")}</em>
                   </div>
                 </div>
               `;
      }).join('')}
           </div>
        </div>
      `;

      modalOverlay.innerHTML = contentHtml;
      modalOverlay.style.display = "flex";

      document.getElementById("close-modal-btn").onclick = () => {
        modalOverlay.style.display = "none";
      };

      // Close on outside click
      modalOverlay.onclick = (e) => {
        if (e.target === modalOverlay) modalOverlay.style.display = "none";
      };

    } catch (e) {
      console.error(e);
      alert("Could not load attempt details.");
    }
  }

  escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  renderStrengthsAndWeaknesses() {
    document.getElementById("strengths-list").innerHTML = this.data.strengths
      .map((s) => `<div class="strength-item">${s}</div>`)
      .join("");

    document.getElementById("weaknesses-list").innerHTML = this.data.weaknesses
      .map((w) => `<div class="weakness-item">${w}</div>`)
      .join("");
  }

  renderLearningPlan() {
    const container = document.getElementById("learning-plan");
    if (!container) return;

    if (!this.data.weakAreas || this.data.weakAreas.length === 0) {
      container.innerHTML = `
        <div class="plan-item">
          <div class="plan-icon">🌟</div>
          <div class="plan-content">
            <div class="plan-title">Keep it up!</div>
            <div class="plan-description">You are doing strong in all topics practiced so far. Try harder difficulties!</div>
          </div>
        </div>`;
      return;
    }

    container.innerHTML = this.data.weakAreas
      .map(
        (area) => `
      <div class="plan-item">
        <div class="plan-icon">📘</div>
        <div class="plan-content">
          <div class="plan-title">Improve ${area.category}</div>
          <div class="plan-description">
            Avg Score: ${area.avg_score}% (${area.question_count} questions)
            <div class="plan-goal">Goal: reach 80%+ in this topic</div>
            ${area.key_points && area.key_points.length
            ? `<ul style="margin-top:5px;padding-left:20px;">
                    ${area.key_points
              .map((p) => `<li>${p}</li>`)
              .join("")}
                  </ul>`
            : ""
          }
            ${area.suggested_actions && area.suggested_actions.length
            ? `<ul style="margin-top:5px;padding-left:20px;">
                    ${area.suggested_actions
              .map((act) => `<li>${act}</li>`)
              .join("")}
                  </ul>`
            : ""
          }
          </div>
        </div>
      </div>
    `
      )
      .join("");
  }
}

new AnalyticsManager();
