const API_BASE = "/api";

async function apiRequest(method, path, body = null, isFormData = false) {
  const token = localStorage.getItem("rpr_token");
  const headers = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (body && !isFormData) headers["Content-Type"] = "application/json";

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: isFormData ? body : (body ? JSON.stringify(body) : null),
  });

  if (res.status === 401) {
    localStorage.removeItem("rpr_token");
    window.location.href = "login.html";
    return;
  }

  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || `Request failed (${res.status})`);
  return data;
}

const api = {
  get:      (path)       => apiRequest("GET",    path),
  post:     (path, body) => apiRequest("POST",   path, body),
  put:      (path, body) => apiRequest("PUT",    path, body),
  delete:   (path)       => apiRequest("DELETE", path),
  postForm: (path, fd)   => apiRequest("POST",   path, fd, true),
};
