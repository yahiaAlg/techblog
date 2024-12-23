// Initialize Date Range Picker
$("#dateRange").daterangepicker({
  opens: "left",
  autoUpdateInput: false,
  locale: {
    cancelLabel: "Clear",
  },
});

$("#dateRange").on("apply.daterangepicker", function (ev, picker) {
  $(this).val(
    picker.startDate.format("MM/DD/YYYY") +
      " - " +
      picker.endDate.format("MM/DD/YYYY")
  );
  applyFilters();
});

// View Toggle
document.querySelectorAll(".view-toggle .btn").forEach((btn) => {
  btn.addEventListener("click", function () {
    document
      .querySelectorAll(".view-toggle .btn")
      .forEach((b) => b.classList.remove("active"));
    this.classList.add("active");

    const view = this.dataset.view;
    const results = document.getElementById("searchResults");
    if (view === "grid") {
      results.classList.add("row-cols-md-2");
    } else {
      results.classList.remove("row-cols-md-2");
    }
  });
});

// Filter Management
let activeFilters = new Set();

function applyFilters() {
  const filters = {
    categories: [...document.querySelectorAll('[name="category"]:checked')].map(
      (cb) => cb.value
    ),
    tags: [...document.querySelectorAll('[name="tag"]:checked')].map(
      (cb) => cb.value
    ),
    authors: [...document.querySelector("select").selectedOptions].map(
      (opt) => opt.value
    ),
    dateRange: document.getElementById("dateRange").value,
  };

  loading.show();

  fetch("/api/search/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
    },
    body: JSON.stringify({
      query: "{{ query }}",
      filters: filters,
      sort: document.getElementById("currentSort").textContent.toLowerCase(),
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      updateResults(data.results);
      updateActiveFilters(filters);
      updateSearchStats(data.total_results, data.search_time);
    })
    .finally(() => {
      loading.hide();
    });
}

function updateResults(results) {
  const container = document.getElementById("searchResults");
  container.innerHTML = "";

  if (results.length === 0) {
    container.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-info">
                        No results found for your search criteria.
                        Try adjusting your filters or search terms.
                    </div>
                </div>
            `;
    return;
  }

  results.forEach((result) => {
    container.insertAdjacentHTML("beforeend", createResultCard(result));
  });
}

function createResultCard(result) {
  return `
            <div class="col-12 ${
              document
                .querySelector('[data-view="grid"]')
                .classList.contains("active")
                ? "col-md-6"
                : ""
            }">
                <article class="result-card">
                    <!-- Result card HTML structure -->
                </article>
            </div>
        `;
}

function updateActiveFilters(filters) {
  const container = document.getElementById("activeFilters");
  container.innerHTML = "";

  Object.entries(filters).forEach(([type, values]) => {
    if (Array.isArray(values)) {
      values.forEach((value) => {
        addFilterBadge(container, type, value);
      });
    } else if (values) {
      addFilterBadge(container, type, values);
    }
  });
}

function addFilterBadge(container, type, value) {
  const badge = document.createElement("div");
  badge.className = "filter-badge";
  badge.innerHTML = `
            ${type}: ${value}
            <span class="remove-filter" onclick="removeFilter('${type}', '${value}')">
                <i class="fas fa-times"></i>
            </span>
        `;
  container.appendChild(badge);
}

function removeFilter(type, value) {
  if (type === "category") {
    document.querySelector(
      `[name="category"][value="${value}"]`
    ).checked = false;
  } else if (type === "tag") {
    document.querySelector(`[name="tag"][value="${value}"]`).checked = false;
  } else if (type === "dateRange") {
    document.getElementById("dateRange").value = "";
  }
  applyFilters();
}

function resetFilters() {
  document
    .querySelectorAll('input[type="checkbox"]')
    .forEach((cb) => (cb.checked = false));
  document.querySelector("select").selectedIndex = -1;
  document.getElementById("dateRange").value = "";
  applyFilters();
}

new Chart(ctx, {
  type: "line",
  data: {
    labels: trendsData.labels,
    datasets: [
      {
        label: "Search Volume",
        data: trendsData.data,
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

// Load More Results
let currentPage = 1;
const loadMoreBtn = document.getElementById("loadMoreBtn");

if (loadMoreBtn) {
  loadMoreBtn.addEventListener("click", () => {
    currentPage++;
    loading.show();

    const currentFilters = {
      categories: [
        ...document.querySelectorAll('[name="category"]:checked'),
      ].map((cb) => cb.value),
      tags: [...document.querySelectorAll('[name="tag"]:checked')].map(
        (cb) => cb.value
      ),
      authors: [...document.querySelector("select").selectedOptions].map(
        (opt) => opt.value
      ),
      dateRange: document.getElementById("dateRange").value,
    };

    fetch(`/api/search/?page=${currentPage}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
          .value,
      },
      body: JSON.stringify({
        query: "{{ query }}",
        filters: currentFilters,
        sort: document.getElementById("currentSort").textContent.toLowerCase(),
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        const container = document.getElementById("searchResults");
        data.results.forEach((result) => {
          container.insertAdjacentHTML("beforeend", createResultCard(result));
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
