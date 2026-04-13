let pollInterval = null;

async function pollStatus(jobId) {
  try {
    const job = await api.get(`/status/${jobId}`);
    updateUI(job);

    if (job.status === "completed") {
      clearInterval(pollInterval);
      setTimeout(() => {
        window.location.href = `result.html?job_id=${jobId}`;
      }, 1500);
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
      `<li><span class="step">[${l.step}]</span> ${l.message}</li>`
    ).join("");
    list.scrollTop = list.scrollHeight;
  } catch (_) {}
}

function updateUI(job) {
  const statusEl = document.getElementById("status-badge");
  const progressFill = document.getElementById("progress-fill");
  const progressText = document.getElementById("progress-text");
  const statusMsg = document.getElementById("status-msg");

  if (statusEl) {
    statusEl.textContent = job.status;
    statusEl.className = `badge badge-${job.status}`;
  }

  const progress = job.progress || 0;
  if (progressFill) progressFill.style.width = `${progress}%`;
  if (progressText) progressText.textContent = `${progress}%`;

  const messages = {
    queued: "Your document is queued for processing...",
    parsing: "Extracting text from document...",
    splitting: "Splitting into sections...",
    processing: `Refining sections with AI... ${progress}%`,
    completed: "✅ Refinement complete! Redirecting...",
    failed: `❌ Processing failed: ${job.error || "Unknown error"}`
  };
  if (statusMsg) statusMsg.textContent = messages[job.status] || job.status;
}

function initProcessing() {
  const params = new URLSearchParams(window.location.search);
  const jobId = params.get("job_id");
  if (!jobId) {
    window.location.href = "dashboard.html";
    return;
  }

  document.getElementById("job-id-display").textContent = jobId;
  pollStatus(jobId);
  pollLogs(jobId);
  pollInterval = setInterval(() => {
    pollStatus(jobId);
    pollLogs(jobId);
  }, 3000);
}
