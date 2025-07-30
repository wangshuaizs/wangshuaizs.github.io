document.addEventListener("DOMContentLoaded", () => {
  const tabs = document.querySelectorAll(".tab");
  const contents = document.querySelectorAll(".tab-content");

  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const targetTab = tab.getAttribute("data-tab");

      // Hide all tabs content
      contents.forEach(content => {
        content.classList.remove("active");
      });

      // Show the selected tab content
      document.getElementById(targetTab).classList.add("active");

      // Highlight the active tab
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
    });
  });

  // Set the first tab to active by default
  tabs[0].classList.add("active");
  contents[0].classList.add("active");
});
