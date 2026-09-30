document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("comicForm");
  const button = document.getElementById("generateButton");
  if (!form || !button) return;

  form.addEventListener("submit", () => {
    button.disabled = true;
    button.textContent = "✨ Creating your comic… please wait";
  });
});
