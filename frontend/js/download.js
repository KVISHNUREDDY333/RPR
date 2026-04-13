async function initResult() {
  const params = new URLSearchParams(window.location.search);
  const jobId = params.get("job_id");
  if (!jobId) { window.location.href = "/pages/dashboard.html"; return; }

  try {
    const job = await api.get(`/status/${jobId}`);
    document.getElementById("filename").textContent = job.original_filename || "Document";
    document.getElementById("word-count").textContent = job.word_count || "-";
    document.getElementById("proc-time").textContent = job.processing_time ? `${job.processing_time}s` : "-";
    document.getElementById("similarity").textContent = job.similarity_score != null
      ? `${(job.similarity_score * 100).toFixed(1)}%` : "-";
  } catch (err) {
    alert("Failed to load result: " + err.message);
    return;
  }

  document.getElementById("download-btn").addEventListener("click", () => {
    const token = localStorage.getItem("rpr_token");
    const url = `/api/download/${jobId}?token=${encodeURIComponent(token)}`;
    const a = document.createElement("a");
    a.href = url;
    a.download = "";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  });
}
