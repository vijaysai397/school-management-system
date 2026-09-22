document.addEventListener('DOMContentLoaded', () => {
    const signupForm = document.querySelector('#signup-form');

    if (!signupForm) {
        return;
    }

    signupForm.addEventListener('submit', (event) => {
        const password = document.querySelector('#password');
        const confirmPassword = document.querySelector('#confirm_password');

        if (password.value !== confirmPassword.value) {
            event.preventDefault();
            confirmPassword.setCustomValidity('Passwords do not match.');
            confirmPassword.reportValidity();
        } else {
            confirmPassword.setCustomValidity('');
        }
    });
});
