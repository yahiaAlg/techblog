function updatePasswordStrength(password) {
  let strength = 0;

  if (password.length >= 8) strength++;
  if (/[A-Z]/.test(password)) strength++;
  if (/[a-z]/.test(password)) strength++;
  if (/[0-9]/.test(password)) strength++;
  if (/[^A-Za-z0-9]/.test(password)) strength++;

  const strengthBar = document.getElementById("passwordStrength");
  const strengthText = document.getElementById("passwordStrengthText");

  switch (strength) {
    case 0:
    case 1:
      strengthBar.style.width = "20%";
      strengthBar.className = "progress-bar bg-danger";
      strengthText.textContent = "Very Weak";
      break;
    case 2:
      strengthBar.style.width = "40%";
      strengthBar.className = "progress-bar bg-warning";
      strengthText.textContent = "Weak";
      break;
    case 3:
      strengthBar.style.width = "60%";
      strengthBar.className = "progress-bar bg-info";
      strengthText.textContent = "Medium";
      break;
    case 4:
      strengthBar.style.width = "80%";
      strengthBar.className = "progress-bar bg-primary";
      strengthText.textContent = "Strong";
      break;
    case 5:
      strengthBar.style.width = "100%";
      strengthBar.className = "progress-bar bg-success";
      strengthText.textContent = "Very Strong";
      break;
  }
}

password1Input.addEventListener("input", function () {
  updatePasswordStrength(this.value);
});

// Password match indicator
password2Input.addEventListener("input", function () {
  const matchIndicator = document.getElementById("passwordMatch");
  if (this.value === password1Input.value) {
    matchIndicator.textContent = "Passwords match";
    matchIndicator.className = "text-success small";
  } else {
    matchIndicator.textContent = "Passwords do not match";
    matchIndicator.className = "text-danger small";
  }
});

// Form validation
document.querySelector("form").addEventListener("submit", function (e) {
  if (!this.checkValidity()) {
    e.preventDefault();
    e.stopPropagation();
  }
  this.classList.add("was-validated");
});


/* add a class="form-control" to each input field */
document.querySelectorAll("input").forEach((input) => { input.classList.add("form-control"); });
/* add a class="form-check-input" class="form-check-label" to each checkbox and the label next to it */
document.querySelectorAll("input[type='checkbox']").forEach((checkbox) => { checkbox.classList.add("form-check-input"); });



