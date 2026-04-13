function requireAuth() {
  if (!localStorage.getItem("rpr_token")) {
    window.location.href = "login.html";
  }
}

function logout() {
  localStorage.removeItem("rpr_token");
  window.location.href = "login.html";
}

async function handleLogin(e) {
  e.preventDefault();
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const errEl = document.getElementById("error");
  const btn = document.getElementById("submit-btn");

  errEl.classList.add("hidden");
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Signing in...';

  try {
    const data = await api.post("/auth/login", { email, password });
    localStorage.setItem("rpr_token", data.access_token);
    window.location.href = "dashboard.html";
  } catch (err) {
    errEl.textContent = err.message;
    errEl.classList.remove("hidden");
    btn.disabled = false;
    btn.textContent = "Sign In";
  }
}

async function handleSignup(e) {
  e.preventDefault();
  const name = document.getElementById("name").value;
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const errEl = document.getElementById("error");
  const btn = document.getElementById("submit-btn");

  errEl.classList.add("hidden");
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Creating account...';

  try {
    const data = await api.post("/auth/signup", { name, email, password });
    localStorage.setItem("rpr_token", data.access_token);
    window.location.href = "dashboard.html";
  } catch (err) {
    errEl.textContent = err.message;
    errEl.classList.remove("hidden");
    btn.disabled = false;
    btn.textContent = "Create Account";
  }
}
