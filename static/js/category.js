// Filter Management
let activeFilters = new Set();

function applyFilters() {
  const type = document.getElementById("filterType").value;
  const level = document.getElementById("filterLevel").value;

  if (type) addFilter("type", type);
  if (level) addFilter("level", level);

  updateCategoryGrid();
  updateActiveFiltersDisplay();
}

function addFilter(key, value) {
  activeFilters.add(`${key}:${value}`);
}

function removeFilter(filter) {
  activeFilters.delete(filter);
  updateCategoryGrid();
  updateActiveFiltersDisplay();
}

function updateActiveFiltersDisplay() {
  const container = document.getElementById("activeFilters");
  container.innerHTML = "";

  activeFilters.forEach((filter) => {
    const [key, value] = filter.split(":");
    const badge = document.createElement("div");
    badge.className = "filter-badge";
    badge.innerHTML = `
                ${key}: ${value}
                <span class="remove-filter" onclick="removeFilter('${filter}')">
                    <i class="fas fa-times"></i>
                </span>
            `;
    container.appendChild(badge);
  });
}

function updateCategoryGrid() {
  const cards = document.querySelectorAll("#categoryGrid > div");
  let visibleCount = 0;

  cards.forEach((card) => {
    let shouldShow = true;

    activeFilters.forEach((filter) => {
      const [key, value] = filter.split(":");
      if (card.dataset[key] !== value) {
        shouldShow = false;
      }
    });

    if (shouldShow) {
      card.style.display = "";
      card.classList.add("animate-fade-in");
      visibleCount++;
    } else {
      card.style.display = "none";
    }
  });

  // Show/hide no results message
  const noResults = document.querySelector(".alert-info");
  if (noResults) {
    noResults.style.display = visibleCount === 0 ? "" : "none";
  }
}

// Sorting
function sortCategories(method) {
  const grid = document.getElementById("categoryGrid");
  const cards = Array.from(grid.children);

  cards.sort((a, b) => {
    switch (method) {
      case "latest":
        return new Date(b.dataset.date) - new Date(a.dataset.date);
      case "popular":
        return parseInt(b.dataset.views) - parseInt(a.dataset.views);
      case "articles":
        return parseInt(b.dataset.articles) - parseInt(a.dataset.articles);
      case "alphabetical":
        return a.dataset.name.localeCompare(b.dataset.name);
    }
  });

  cards.forEach((card) => grid.appendChild(card));
  document.getElementById("currentSort").textContent =
    method.charAt(0).toUpperCase() + method.slice(1);
}

// Load More Functionality
let currentPage = 1;
const loadMoreBtn = document.getElementById("loadMoreBtn");

if (loadMoreBtn) {
  loadMoreBtn.addEventListener("click", () => {
    currentPage++;
    loading.show();

    fetch(`/api/categories/?page=${currentPage}`)
      .then((response) => response.json())
      .then((data) => {
        const grid = document.getElementById("categoryGrid");

        data.results.forEach((category) => {
          const categoryHtml = createCategoryCard(category);
          grid.insertAdjacentHTML("beforeend", categoryHtml);
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

function createCategoryCard(category) {
  return `
            <div class="col-md-6 col-lg-4" 
                 data-category="${category.type}" 
                 data-level="${category.level}"
                 data-date="${category.created_at}"
                 data-views="${category.view_count}"
                 data-articles="${category.article_count}"
                 data-name="${category.name}">
                <div class="category-card animate-fade-in">
                    <!-- Card content structure similar to Django template -->
                </div>
            </div>
        `;
}

// Initialize tooltips
const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
tooltips.forEach((tooltip) => new bootstrap.Tooltip(tooltip));
