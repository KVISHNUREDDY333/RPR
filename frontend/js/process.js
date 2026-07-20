async function initDashboard() {
  // Load user info
  try {
    const user = await api.get("/auth/me");
    document.getElementById("user-name").textContent = user.name;
    const avatar = document.getElementById("profile-avatar");
    if (avatar) avatar.textContent = user.name.charAt(0).toUpperCase();
    const pName = document.getElementById("profile-name");
    const pEmail = document.getElementById("profile-email");
    const newName = document.getElementById("new-name");
    if (pName) pName.textContent = user.name;
    if (pEmail) pEmail.textContent = user.email;
    if (newName) newName.value = user.name;
  } catch (_) {}

  // Load stats
  try {
    const stats = await api.get("/auth/stats");
    const fmt = n => n >= 1000 ? (n / 1000).toFixed(1) + "k" : String(n);
    ["total","completed"].forEach(k => {
      const el = document.getElementById("stat-" + k);
      const el2 = document.getElementById("p-" + k);
      const val = stats[k === "total" ? "total_jobs" : k];
      if (el) el.textContent = val;
      if (el2) el2.textContent = val;
    });
    const words = fmt(stats.total_words_processed || 0);
    const score = stats.avg_score != null ? stats.avg_score + "/10" : "—";
    ["stat-words","p-words"].forEach(id => { const e = document.getElementById(id); if (e) e.textContent = words; });
    ["stat-score","p-score"].forEach(id => { const e = document.getElementById(id); if (e) e.textContent = score; });
  } catch (_) {}

  // Load jobs
  await loadJobs();

  // Profile form
  const profileForm = document.getElementById("profile-form");
  if (profileForm) {
    profileForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const msgEl = document.getElementById("profile-msg");
      const name = document.getElementById("new-name").value.trim();
      const curPwd = document.getElementById("cur-password").value;
      const newPwd = document.getElementById("new-password").value;
      const body = {};
      if (name) body.name = name;
      if (newPwd) { body.current_password = curPwd; body.new_password = newPwd; }
      if (!Object.keys(body).length) return;
      try {
        await api.put("/auth/profile", body);
        msgEl.className = "alert alert-success";
        msgEl.textContent = "Profile updated successfully!";
        msgEl.classList.remove("hidden");
        document.getElementById("user-name").textContent = name || document.getElementById("user-name").textContent;
        document.getElementById("cur-password").value = "";
        document.getElementById("new-password").value = "";
      } catch (err) {
        msgEl.className = "alert alert-error";
        msgEl.textContent = err.message;
        msgEl.classList.remove("hidden");
      }
      setTimeout(() => msgEl.classList.add("hidden"), 4000);
    });
  }
}

async function loadJobs() {
  try {
    const jobs = await api.get("/jobs");
    const tbody = document.getElementById("jobs-tbody");
    const empty = document.getElementById("jobs-empty");
    const table = document.getElementById("jobs-table");
    if (!jobs.length) {
      if (empty) empty.classList.remove("hidden");
      if (table) table.style.display = "none";
      return;
    }
    if (empty) empty.classList.add("hidden");
    if (table) table.style.display = "table";
    tbody.innerHTML = jobs.map(j => {
      const score = j.overall_score != null ? `<span class="score-badge">${j.overall_score}/10</span>` : "—";
      const words = j.word_count ? j.word_count.toLocaleString() : "—";
      const date = new Date(j.created_at).toLocaleDateString();
      let action = "";
      if (j.status === "completed") {
        action = `<a href="result.html?job_id=${j.job_id}" class="btn btn-outline btn-sm">View</a>`;
      } else if (j.status === "failed") {
        action = `<span class="text-error text-xs">Failed</span>`;
      } else {
        action = `<a href="processing.html?job_id=${j.job_id}" class="btn btn-outline btn-sm">Track</a>`;
      }
      return `<tr>
        <td class="filename-cell" title="${j.original_filename || ''}">${j.original_filename || "—"}</td>
        <td><span class="badge badge-${j.status}">${j.status}</span></td>
        <td>${score}</td>
        <td>${words}</td>
        <td>${date}</td>
        <td><div class="job-actions">${action}<button class="btn btn-danger btn-sm" onclick="deleteJob('${j.job_id}', this)">✕</button></div></td>
      </tr>`;
    }).join("");
  } catch (err) {
    console.error("Failed to load jobs:", err);
  }
}

async function deleteJob(jobId, btn) {
  if (!confirm("Delete this job? This cannot be undone.")) return;
  btn.disabled = true;
  try {
    await api.delete("/jobs/" + jobId);
    await loadJobs();
    // Refresh stats
    const stats = await api.get("/auth/stats");
    const el = document.getElementById("stat-total");
    if (el) el.textContent = stats.total_jobs;
  } catch (err) {
    alert("Delete failed: " + err.message);
    btn.disabled = false;
  }
}
