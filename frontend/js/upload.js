function initUpload() {
  const zone = document.getElementById("upload-zone");
  const fileInput = document.getElementById("file-input");
  const uploadBtn = document.getElementById("upload-btn");
  const fileInfo = document.getElementById("file-info");
  let selectedFile = null;

  zone.addEventListener("click", () => fileInput.click());

  zone.addEventListener("dragover", (e) => {
    e.preventDefault();
    zone.classList.add("drag-over");
  });
  zone.addEventListener("dragleave", () => zone.classList.remove("drag-over"));
  zone.addEventListener("drop", (e) => {
    e.preventDefault();
    zone.classList.remove("drag-over");
    if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files[0]) handleFile(fileInput.files[0]);
  });

  function handleFile(file) {
    const allowed = [".pdf", ".docx", ".doc", ".txt"];
    const ext = "." + file.name.split(".").pop().toLowerCase();
    if (!allowed.includes(ext)) {
      alert("Only PDF, DOCX, DOC, TXT files are supported.");
      return;
    }
    if (file.size > 20 * 1024 * 1024) {
      alert("File too large. Maximum size is 20MB.");
      return;
    }
    selectedFile = file;
    fileInfo.textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
    fileInfo.classList.remove("hidden");
    uploadBtn.disabled = false;
  }

  uploadBtn.addEventListener("click", async () => {
    if (!selectedFile) return;
    const formData = new FormData();
    formData.append("file", selectedFile);

    uploadBtn.disabled = true;
    uploadBtn.innerHTML = '<span class="spinner"></span> Uploading...';

    try {
      const data = await api.postForm("/upload", formData);
      window.location.href = `processing.html?job_id=${data.job_id}`;
    } catch (err) {
      alert("Upload failed: " + err.message);
      uploadBtn.disabled = false;
      uploadBtn.textContent = "Start Refinement";
    }
  });
}
