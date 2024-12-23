new Chart(ctx, {
  type: "line",
  data: {
    labels: activityData.labels,
    datasets: [
      {
        label: "Articles Published",
        data: activityData.articles,
        borderColor: "rgb(189, 147, 244)",
        tension: 0.3,
        fill: false,
      },
    ],
  },
  options: {
    responsive: true,
    plugins: {
      legend: {
        position: "top",
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: "rgba(255, 255, 255, 0.1)",
        },
      },
      x: {
        grid: {
          color: "rgba(255, 255, 255, 0.1)",
        },
      },
    },
  },
});

// Load More Articles
let currentPage = 1;
const loadMoreBtn = document.getElementById("loadMoreBtn");

if (loadMoreBtn) {
  loadMoreBtn.addEventListener("click", () => {
    currentPage++;
    loading.show();

    fetch(`/api/authors/{{ author.username }}/articles/?page=${currentPage}`)
      .then((response) => response.json())
      .then((data) => {
        const container = document.querySelector(".row.g-4");

        data.results.forEach((article) => {
          const articleHtml = createArticleCard(article);
          container.insertAdjacentHTML("beforeend", articleHtml);
        });

        if (!data.has_next) {
          loadMoreBtn.style.display = "none";
        }
      })
      .finally(() => {
        loading.hide();
      });
  });
}

function createArticleCard(article) {
  return `
            <div class="col-md-6">
                <article class="article-card">
                    <img src="${article.featured_image}" class="article-image w-100" alt="${article.title}" loading="lazy">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <a href="/category/${article.category.slug}/" class="badge bg-primary text-decoration-none">
                                ${article.category.name}
                            </a>
                            <small class="text-muted">${article.created_at}</small>
                        </div>
                        <h5 class="card-title">
                            <a href="/article/${article.slug}/" class="text-decoration-none">
                                ${article.title}
                            </a>
                        </h5>
                        <p class="card-text">${article.excerpt}</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <div class="d-flex gap-3">
                                <span><i class="far fa-eye me-1"></i>${article.view_count}</span>
                                <span><i class="far fa-comment me-1"></i>${article.comment_count}</span>
                            </div>
                            <a href="/article/${article.slug}/" class="btn btn-primary btn-sm">Read More</a>
                        </div>
                    </div>
                </article>
            </div>
        `;
}

// Contact Form Handler
const contactForm = document.getElementById("contactForm");
if (contactForm) {
  contactForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const formData = new FormData(this);

    fetch("/api/authors/{{ author.username }}/contact/", {
      method: "POST",
      headers: {
        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
          .value,
      },
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        showToast(data.message, data.success ? "success" : "error");
        if (data.success) {
          this.reset();
        }
      });
  });
}
