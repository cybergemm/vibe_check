document.addEventListener('DOMContentLoaded', function () {
  const toggleIcons = document.querySelectorAll('.toggle-password');

  toggleIcons.forEach(icon => {
    icon.addEventListener('click', function () {
      const input = document.getElementById(this.dataset.toggle);
      const isVisible = input.type === 'text';
      input.type = isVisible ? 'password' : 'text';
      this.classList.toggle('bi-eye');
      this.classList.toggle('bi-eye-slash');
    });
  });
});