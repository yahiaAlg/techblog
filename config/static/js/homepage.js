// Featured Slider
(function () {
  const slides = document.querySelectorAll(".featured-slide");
  let currentSlide = 0;

  function showSlide(index) {
    slides.forEach((slide) => slide.classList.remove("active"));
    slides[index].classList.add("active");
  }

  function nextSlide() {
    currentSlide = (currentSlide + 1) % slides.length;
    showSlide(currentSlide);
  }

  function previousSlide() {
    currentSlide = (currentSlide - 1 + slides.length) % slides.length;
    showSlide(currentSlide);
  }

  document
    .querySelector(".carousel-control-next")
    .addEventListener("click", nextSlide);
  document
    .querySelector(".carousel-control-prev")
    .addEventListener("click", previousSlide);

  setInterval(nextSlide, 5000);
})();

// Infinite Scroll
(function () {
  let page = 1;
  let loading = false;
  const container = document.getElementById("articles-container");
  const loader = document.querySelector(".infinite-scroll-loader");

  function loadMoreArticles() {
    if (loading) return;
    loading = true;
    loader.style.display = "block";

    fetch(`/api/articles/?page=${page + 1}`)
      .then((response) => response.json())
      .then((data) => {
        if (data.results.length > 0) {
          page++;
          data.results.forEach((article) => {
            // Create and append article cards
            const articleHtml = createArticleCard(article);
            container.insertAdjacentHTML("beforeend", articleHtml);
          });
        }
      })
      .finally(() => {
        loading = false;
        loader.style.display = "none";
      });
  }

  function createArticleCard(article) {
    return `
                <div class="col-md-6 col-lg-4">
                    <article class="card article-card h-100">
                        <!-- Article card HTML structure -->
                    </article>
                </div>
            `;
  }

  // Intersection Observer for infinite scroll
  const observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting) {
      loadMoreArticles();
    }
  });

  observer.observe(loader);
})();

// Newsletter Form
document
  .getElementById("newsletter-form")
  .addEventListener("submit", function (e) {
    e.preventDefault();
    const email = this.querySelector('input[type="email"]').value;

    fetch("/api/newsletter/subscribe/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
          .value,
      },
      body: JSON.stringify({ email }),
    })
      .then((response) => response.json())
      .then((data) => {
        showToast(data.message, data.success ? "success" : "error");
      });
  });
