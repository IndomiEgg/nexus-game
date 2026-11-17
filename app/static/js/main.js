// Animasi fade-in saat scroll + tombol "Muat lebih banyak".
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add("in");
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.08 });

const observeAll = (root = document) =>
  root.querySelectorAll(".reveal:not(.in)").forEach((el) => observer.observe(el));
observeAll();

document.querySelectorAll("[data-more]").forEach((button) => {
  const grid = document.getElementById(button.dataset.target);
  let page = 1;
  button.addEventListener("click", async () => {
    page += 1;
    button.disabled = true;
    const params = new URLSearchParams({ page, cat: button.dataset.cat || "", q: button.dataset.q || "" });
    try {
      const response = await fetch(`/feed?${params}`);
      grid.insertAdjacentHTML("beforeend", await response.text());
      observeAll(grid);
      if (response.headers.get("X-Has-More") !== "1") button.hidden = true;
    } catch {
      page -= 1;
    }
    button.disabled = false;
  });
});
