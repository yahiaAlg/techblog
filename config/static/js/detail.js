// Reading Progress
(function () {
  const progressBar = document.getElementById("readingProgress");
  window.addEventListener("scroll", () => {
    const winScroll = document.documentElement.scrollTop;
    const height =
      document.documentElement.scrollHeight -
      document.documentElement.clientHeight;
    const scrolled = (winScroll / height) * 100;
    progressBar.style.width = scrolled + "%";
  });
})();

// Table of Contents
(function () {
  const content = document.querySelector(".article-content");
  const toc = document.querySelector("#tableOfContents ul");
  const headings = content.querySelectorAll("h2, h3, h4");

  headings.forEach((heading, index) => {
    const id = `heading-${index}`;
    heading.id = id;

    const li = document.createElement("li");
    li.className = "toc-item";
    li.innerHTML = `<a href="#${id}" class="text-decoration-none">${heading.textContent}</a>`;
    toc.appendChild(li);
  });

  // Highlight current section
  const tocItems = document.querySelectorAll(".toc-item");
  const observerOptions = {
    rootMargin: "-70px 0px -70%",
    threshold: 1.0,
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      const id = entry.target.getAttribute("id");
      const tocItem = document.querySelector(
        `.toc-item a[href="#${id}"]`
      ).parentElement;

      if (entry.isIntersecting) {
        tocItems.forEach((item) => item.classList.remove("active"));
        tocItem.classList.add("active");
      }
    });
  }, observerOptions);

  headings.forEach((heading) => observer.observe(heading));
})();

// Social Sharing
function shareArticle(platform) {
  const url = encodeURIComponent(window.location.href);
  const title = encodeURIComponent(document.title);

  const shareUrls = {
    twitter: `https://twitter.com/intent/tweet?url=${url}&text=${title}`,
    facebook: `https://www.facebook.com/sharer/sharer.php?u=${url}`,
    linkedin: `https://www.linkedin.com/shareArticle?url=${url}&title=${title}`,
  };

  window.open(shareUrls[platform], "_blank", "width=600,height=400");
}

// Copy Link
function copyLink() {
  navigator.clipboard
    .writeText(window.location.href)
    .then(() => showToast("Link copied to clipboard", "success"));
}

// Bookmark Handler
document
  .getElementById("bookmarkButton")
  .addEventListener("click", function () {
    if (!this.classList.contains("bookmarked")) {
      fetch("/api/bookmarks/add/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
            .value,
        },
        body: JSON.stringify({
          article_id: "{{ article.id }}",
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            this.classList.add("bookmarked");
            this.querySelector("i").classList.remove("far");
            this.querySelector("i").classList.add("fas");
            showToast("Article bookmarked", "success");
          }
        });
    }
  });

// Comments Handling
const commentForm = document.getElementById("commentForm");
if (commentForm) {
  commentForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const content = this.querySelector("textarea").value;

    fetch("/api/comments/add/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
          .value,
      },
      body: JSON.stringify({
        article_id: "{{ article.id }}",
        content: content,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          location.reload();
        }
      });
  });
}

function replyToComment(commentId) {
  // Implementation for reply functionality
}

function editComment(commentId) {
  // Implementation for edit functionality
}

function deleteComment(commentId) {
  if (confirm("Are you sure you want to delete this comment?")) {
    fetch(`/api/comments/${commentId}/delete/`, {
      method: "DELETE",
      headers: {
        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
          .value,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          location.reload();
        }
      });
  }
}
