/**
 * MediTrack AI - Main JavaScript
 * Minimal, clean client-side helpers.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Alert dismiss handler
  document.querySelectorAll('.alert-close').forEach(button => {
    button.addEventListener('click', () => {
      const alert = button.closest('.alert');
      if (alert) {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 200);
      }
    });
  });

  // Safety Checker Quick-Select Helper
  const medSelectCheckboxes = document.querySelectorAll('.safety-med-checkbox');
  const customMedsInput = document.getElementById('custom_medicines');

  if (medSelectCheckboxes.length > 0 && customMedsInput) {
    medSelectCheckboxes.forEach(cb => {
      cb.addEventListener('change', () => {
        // Optional quick indicator
      });
    });
  }
});
