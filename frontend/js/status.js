let pollInterval = null;

const STATUS_MESSAGES = {
  queued:     "Queued — waiting to start...",
  parsing:    "Parsing document...",
  splitting:  "Analyzing structure...",
  processing: "AI is reviewing and refining sections...",
  finalizing: "Generating feedback and report...",
  completed:  "Complete! Redirecting to results...",
  failed:     "Processing failed."
};

async function pollStatus(jobId) {
  try {
    const job = await api.get(`/status/${jobId}`);
    updateUI(job);
    if (job.status === "completed") {
      clearInterval(pollInterval);
      setTimeout(() => { window.location.href = `result.html?job_id=${jobId}`; }, 1200);
    } else if (job.status === "failed") {
      clearInterval(pollInterval);
    }
  } catch (err) {
    console.error("Poll error:", err);
  }
}

async function pollLogs(jobId) {
  try {
    const logs = await api.get(`/process/${jobId}/logs`);
    const list = document.getElementById("log-list");
    if (!list || !logs.length) return;
    list.innerHTML = logs.map(l =>
      `<li><span class="step">[${l.step}]</span>${l.message}</li>`
    ).join("");
    list.scrollTop = list.scrollHeight;
  } catch (_) {}
}

function updateUI(job) {
  const badge = document.getElementById("status-badge");
  const fill  = document.getElementById("progress-fill");
  const pct   = document.getElementById("progress-text");
  const msg   = document.getElementById("status-msg");

  if (badge) { badge.textContent = job.status; badge.className = `badge badge-${job.status}`; }

  const progress = job.progress || 0;
  if (fill) fill.style.width = `${progress}%`;
  if (pct)  pct.textContent  = `${progress}%`;
  if (msg)  msg.textContent  = job.status === "failed"
    ? `Failed: ${job.error || "Unknown error"}`
    : (STATUS_MESSAGES[job.status] || job.status);
}

function initProcessing() {
  const params = new URLSearchParams(window.location.search);
  const jobId = params.get("job_id");
  if (!jobId) { window.location.href = "dashboard.html"; return; }

  const display = document.getElementById("job-id-display");
  if (display) display.textContent = jobId;

  pollStatus(jobId);
  pollLogs(jobId);
  pollInterval = setInterval(() => { pollStatus(jobId); pollLogs(jobId); }, 2500);
}
