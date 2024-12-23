// Profile image preview
document
  .querySelector('input[type="file"]')
  .addEventListener("change", function (e) {
    if (e.target.files && e.target.files[0]) {
      const reader = new FileReader();
      reader.onload = function (e) {
        document.querySelector(".profile-avatar").src = e.target.result;
      };
      reader.readAsDataURL(e.target.files[0]);
    }
  });

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
