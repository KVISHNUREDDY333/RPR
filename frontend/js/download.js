async function initResultV2() {
  const params = new URLSearchParams(window.location.search);
  const jobId = params.get("job_id");
  if (!jobId) { window.location.href = "dashboard.html"; return; }

  try {
    const job = await api.get(`/status/${jobId}`);
    if (job.status !== "completed") {
      window.location.href = `processing.html?job_id=${jobId}`;
      return;
    }

    // Populate Overall Score
    document.getElementById("overall-score").textContent = job.overall_score || "0.0";
    document.getElementById("filename-display").textContent = job.original_filename || "Document Analysis";

    // Populate Sections
    const sectionsContainer = document.getElementById("sections-container");
    sectionsContainer.innerHTML = (job.analysis || []).map(s => `
      <div class="section-card">
        <div class="flex-center-between">
          <strong class="text-14">${s.title}</strong>
          <span class="text-primary font-bold">${s.score}/10</span>
        </div>
        <div class="progress-mini">
          <div class="progress-mini-fill" style="width: ${s.score * 10}%"></div>
        </div>
        <p class="text-12 text-muted mt-4">${s.reason}</p>
        <div class="tag-list">
          <span class="tag">Clarity: ${s.clarity}</span>
          ${(s.issues || []).map(issue => `<span class="tag">Issue: ${issue}</span>`).join("")}
        </div>
      </div>
    `).join("");

    // Populate Feedback Lists
    const feedback = job.feedback || {};
    populateList("strengths-list", feedback.strengths);
    populateList("weaknesses-list", feedback.weaknesses);
    populateList("suggestions-list", feedback.suggestions);

    // Setup Downloads
    setupDownloadButton("download-refined", jobId, "refined");
    setupDownloadButton("download-report", jobId, "report");

  } catch (err) {
    alert("Failed to load result: " + err.message);
  }
}

function populateList(id, items) {
  const el = document.getElementById(id);
  if (!items || !items.length) {
    el.innerHTML = '<li class="text-muted">No data available</li>';
    return;
  }
  el.innerHTML = items.map(item => `<li>${item}</li>`).join("");
}

function setupDownloadButton(id, jobId, type) {
  const btn = document.getElementById(id);
  btn.addEventListener("click", () => {
    const token = localStorage.getItem("rpr_token");
    const url = `/api/download/${jobId}?type=${type}&token=${encodeURIComponent(token)}`;
    const a = document.createElement("a");
    a.href = url;
    a.target = "_blank"; // Open in new tab for download
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  });
}
