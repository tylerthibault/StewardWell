// Basic JavaScript for StewardWell

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });

    // Format family code input to uppercase
    const familyCodeInput = document.getElementById('family_code');
    if (familyCodeInput) {
        familyCodeInput.addEventListener('input', function() {
            this.value = this.value.toUpperCase();
        });
    }
});
document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const toggle = document.getElementById('sidebarToggle');
    if (sidebar && toggle) {
        toggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }
});
