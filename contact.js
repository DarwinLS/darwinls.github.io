document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('contactForm');
    const statusMsg = document.getElementById('formStatus');

    form.addEventListener('submit', (e) => {
        e.preventDefault();

        // 1. Validation Logic
        let isValid = true;
        const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
        
        inputs.forEach(input => {
            const group = input.parentElement;
            
            // Check emptiness
            if (!input.value.trim()) {
                setError(input, true);
                isValid = false;
            } else {
                setError(input, false);
            }
        });

        // Check Email specifically
        const emailInput = document.getElementById('email');
        if (emailInput.value && !isValidEmail(emailInput.value)) {
            setError(emailInput, true);
            isValid = false;
        }

        if (!isValid) return;

        // 2. Simulate Sending
        const btn = form.querySelector('.submit-btn');
        const originalText = btn.innerHTML;
        
        btn.disabled = true;
        btn.innerHTML = '<span>Sending...</span>';

        setTimeout(() => {
            // Success State
            statusMsg.textContent = "Thanks! Your message has been sent successfully.";
            statusMsg.className = "form-status success";
            
            form.reset();
            
            // Reset Button
            btn.disabled = false;
            btn.innerHTML = originalText;
            
            // Clear success message after 5s
            setTimeout(() => {
                statusMsg.textContent = "";
                statusMsg.className = "form-status";
            }, 5000);
            
        }, 1500);
    });

    // Helper: Toggle Error State (Visuals + ARIA)
    function setError(input, isError) {
        const group = input.parentElement;
        if (isError) {
            group.classList.add('invalid');
            input.setAttribute('aria-invalid', 'true');
        } else {
            group.classList.remove('invalid');
            input.setAttribute('aria-invalid', 'false');
        }
    }

    // Helper: Clear error on input
    form.querySelectorAll('input, textarea, select').forEach(input => {
        input.addEventListener('input', () => {
            setError(input, false);
        });
    });

    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }
});