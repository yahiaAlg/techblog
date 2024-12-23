// Form validation
(function () {
  "use strict";
  const forms = document.querySelectorAll(".needs-validation");
  Array.from(forms).forEach((form) => {
    form.addEventListener(
      "submit",
      (event) => {
        if (!form.checkValidity()) {
          event.preventDefault();
          event.stopPropagation();
        }
        form.classList.add("was-validated");
      },
      false
    );
  });
})();

// Show/hide password
document.querySelectorAll(".toggle-password").forEach((button) => {
  button.addEventListener("click", function () {
    const input = document.querySelector(this.getAttribute("toggle"));
    if (input.getAttribute("type") === "password") {
      input.setAttribute("type", "text");
      this.innerHTML = '<i class="fas fa-eye-slash"></i>';
    } else {
      input.setAttribute("type", "password");
      this.innerHTML = '<i class="fas fa-eye"></i>';
    }
  });
});
