// Wait until the entire DOM is loaded before running the script
document.addEventListener('DOMContentLoaded', function () {
  // Select all elements with the class 'toggle-password' (typically eye icons)
  const toggleIcons = document.querySelectorAll('.toggle-password');

  // Attach a click event listener to each toggle icon
  toggleIcons.forEach(icon => {
    icon.addEventListener('click', function () {
      // Get the input field this icon is associated with using data-toggle attribute
      const input = document.getElementById(this.dataset.toggle);

      // Check current visibility state of the input field
      const isVisible = input.type === 'text';

      // Toggle between 'password' and 'text' to show or hide password
      input.type = isVisible ? 'password' : 'text';

      // Swap the icon class to reflect the visibility state
      this.classList.toggle('bi-eye');
      this.classList.toggle('bi-eye-slash');
    });
  });
});