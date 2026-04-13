async function initDashboard() {
  try {
    const user = await api.get("/auth/me");
    document.getElementById("user-name").textContent = user.name;
  } catch (_) {}

  try {
    const jobs = await api.get("/jobs");
    const tbody = document.getElementById("jobs-tbody");
    const empty = document.getElementById("no-jobs");
    const table = document.getElementById("jobs-table");

    if (!jobs.length) {
      empty.classList.remove("hidden");
      return;
    }

    table.classList.remove("hidden");
    tbody.innerHTML = jobs.map(j => `
      <tr>
        <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${j.original_filename || "-"}</td>
        <td><span class="badge badge-${j.status}">${j.status}</span></td>
        <td>${new Date(j.created_at).toLocaleDateString()}</td>
        <td>
          ${j.status === "completed"
            ? `<a href="result.html?job_id=${j.job_id}" class="btn btn-outline" style="padding:6px 12px;font-size:12px;">View</a>`
            : j.status === "failed"
            ? `<span style="color:var(--error);font-size:13px;">Failed</span>`
            : `<a href="processing.html?job_id=${j.job_id}" class="btn btn-outline" style="padding:6px 12px;font-size:12px;">Track</a>`
          }
        </td>
      </tr>
    `).join("");
  } catch (err) {
    console.error("Failed to load jobs:", err);
  }
}
