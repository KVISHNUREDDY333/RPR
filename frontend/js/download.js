async function initResult() {
  const params = new URLSearchParams(window.location.search);
  const jobId = params.get("job_id");
  if (!jobId) { window.location.href = "dashboard.html"; return; }

  try {
    const job = await api.get(`/status/${jobId}`);

    if (job.status !== "completed") {
      window.location.href = `processing.html?job_id=${jobId}`;
      return;
    }

    // Header
    document.getElementById("filename-display").textContent = job.original_filename || "Document";

    // Score ring
    const score = job.overall_score || 0;
    document.getElementById("overall-score").textContent = score;
    const ring = document.getElementById("score-ring");
    if (ring) ring.style.setProperty("--pct", score * 10);

    // Stats
    document.getElementById("word-count").textContent = job.word_count ? job.word_count.toLocaleString() : "—";
    document.getElementById("proc-time").textContent = job.processing_time ? `${job.processing_time}s` : "—";
    const analysis = job.analysis || [];
    document.getElementById("section-count").textContent = analysis.length || "—";

    // Section Analysis
    const container = document.getElementById("sections-container");
    if (analysis.length) {
      container.innerHTML = analysis.map(s => {
        const pct = (s.score || 0) * 10;
        const issues = (s.issues || []).map(i => `<span class="tag tag-issue">${i}</span>`).join("");
        const suggestions = (s.suggestions || []).map(i => `<span class="tag">${i}</span>`).join("");
        return `<div class="section-card">
          <div class="flex-between mb-8">
            <strong class="text-sm">${s.title}</strong>
            <span class="text-primary font-bold">${s.score}/10</span>
          </div>
          <div class="section-score-bar">
            <div class="progress-mini" style="flex:1"><div class="progress-mini-fill" style="width:${pct}%"></div></div>
          </div>
          <p class="text-xs text-muted mt-8">${s.reason || ""}</p>
          <div class="flex-center mt-8" style="gap:6px;">
            <span class="tag">Clarity: ${s.clarity || "—"}</span>
            ${issues}
          </div>
          ${suggestions ? `<div class="tag-list mt-4">${suggestions}</div>` : ""}
        </div>`;
      }).join("");
    } else {
      container.innerHTML = `<div class="empty-state"><p class="text-muted">No section analysis available.</p></div>`;
    }

    // Feedback
    const fb = job.feedback || {};
    if (fb.summary) {
      document.getElementById("summary-box").style.display = "block";
      document.getElementById("summary-text").textContent = fb.summary;
    }
    populateList("strengths-list", fb.strengths, "✅");
    populateList("weaknesses-list", fb.weaknesses, "⚠️");
    populateList("suggestions-list", fb.suggestions, "💡");

    // Downloads
    setupDownload("download-refined", jobId, "refined");
    setupDownload("download-report", jobId, "report");

  } catch (err) {
    alert("Failed to load result: " + err.message);
  }
}

function populateList(id, items, icon) {
  const el = document.getElementById(id);
  if (!el) return;
  if (!items || !items.length) {
    el.innerHTML = `<li class="text-muted text-sm">No data available.</li>`;
    return;
  }
  el.innerHTML = items.map(item => `<li data-icon="${icon || ''}">${item}</li>`).join("");
}

function setupDownload(btnId, jobId, type) {
  const btn = document.getElementById(btnId);
  if (!btn) return;
  btn.addEventListener("click", () => {
    const token = localStorage.getItem("rpr_token");
    const url = `/api/download/${jobId}?type=${type}&token=${encodeURIComponent(token)}`;
    const a = document.createElement("a");
    a.href = url;
    a.target = "_blank";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  });
}
