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

// Save preferences
document
  .getElementById("preferencesForm")
  .addEventListener("change", function (e) {
    const preference = e.target.id;
    const value = e.target.checked;

    fetch("/api/preferences/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
          .value,
      },
      body: JSON.stringify({
        preference: preference,
        value: value,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          showToast("Preferences saved successfully", "success");
        } else {
          showToast("Error saving preferences", "error");
        }
      });
  });

// Copy API key
document.querySelector(".fa-copy").addEventListener("click", function () {
  const apiKey = this.closest(".api-key").textContent.trim();
  navigator.clipboard.writeText(apiKey).then(() => {
    showToast("API key copied to clipboard", "success");
  });
});

// Generate new API key
document
  .querySelector(".btn-outline-primary")
  .addEventListener("click", function () {
    if (
      confirm(
        "Are you sure you want to generate a new API key? The old one will be invalidated."
      )
    ) {
      fetch("/api/generate-key/", {
        method: "POST",
        headers: {
          "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
            .value,
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            document.querySelector(".api-key").textContent = data.key;
            showToast("New API key generated successfully", "success");
          } else {
            showToast("Error generating API key", "error");
          }
        });
    }
  });
