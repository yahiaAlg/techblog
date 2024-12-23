// Theme Toggle
document.getElementById("themeToggle").addEventListener("click", function () {
  const html = document.documentElement;
  const currentTheme = html.getAttribute("data-bs-theme");
  const newTheme = currentTheme === "dark" ? "light" : "dark";
  html.setAttribute("data-bs-theme", newTheme);
  localStorage.setItem("theme", newTheme);
  this.querySelector("i").className =
    newTheme === "dark" ? "fas fa-moon" : "fas fa-sun";
});

// Toast Notification
function showToast(message, type = "info") {
  const toastContainer = document.querySelector(".toast-container");
  const toast = document.createElement("div");
  toast.className = `toast show`;
  toast.innerHTML = `
                <div class="toast-header">
                    <strong class="me-auto">${
                      type.charAt(0).toUpperCase() + type.slice(1)
                    }</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">${message}</div>
            `;
  toastContainer.appendChild(toast);
  setTimeout(() => toast.remove(), 5000);
}

// Loading Overlay
const loading = {
  show: () =>
    (document.querySelector(".loading-overlay").style.display = "flex"),
  hide: () =>
    (document.querySelector(".loading-overlay").style.display = "none"),
};
