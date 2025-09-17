document.addEventListener('DOMContentLoaded', () => {
  // --- Modal Handling ---
  const modalTriggers = document.querySelectorAll('[data-modal-target]');
  const closeButtons = document.querySelectorAll('.close-btn');
  const modalOverlays = document.querySelectorAll('.modal-overlay');

  const openModal = (modalId) => {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.add('active');
  };

  const closeModal = () => {
    document.querySelector('.modal-overlay.active')?.classList.remove('active');
  };

  modalTriggers.forEach((trigger) => {
    trigger.addEventListener('click', (event) => {
      event.preventDefault();
      const modalId = trigger.getAttribute('data-modal-target');
      openModal(modalId);
    });
  });

  closeButtons.forEach((button) =>
    button.addEventListener('click', closeModal)
  );

  modalOverlays.forEach((overlay) => {
    overlay.addEventListener('click', (event) => {
      if (event.target === overlay) closeModal();
    });
  });

  // --- Quick Chat Button ---
  const quickChatBtn = document.getElementById('quickChatBtn');
  if (quickChatBtn) {
    quickChatBtn.addEventListener('click', () => {
      alert('Connecting you to a Quick Chat session as a guest...');
    });
  }

  // --- Form Submission with Fetch API ---
  const registerForm = document.getElementById('registerForm');
  const loginForm = document.getElementById('loginForm'); // Make sure your form has this ID

  if (loginForm) {
    loginForm.addEventListener('submit', async (event) => {
      event.preventDefault(); // Prevents page from reloading

      // --- Step 1: Get the message element and clear it ---
      const messageElement = document.getElementById('loginMessage');
      if (!messageElement) {
        console.error(
          'CRITICAL: The HTML element with id="loginMessage" was not found.'
        );
        return; // Stop execution if the message element is missing
      }
      messageElement.textContent = ''; // Clear previous messages

      // --- Step 2: Prepare and send the request ---
      const formData = new FormData(loginForm);
      const data = Object.fromEntries(formData.entries());

      try {
        const response = await fetch(
          'http://127.0.0.1:8002/api/v1/auth/login',
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
          }
        );

        const responseData = await response.json();

        if (!response.ok) {
          // Use the detailed error message from the server if available
          throw new Error(
            responseData.detail ||
              'Login failed. Please check your credentials.'
          );
        }

        // --- Step 3: Handle the successful login ---
        console.log('Login successful:', responseData);

        // Store tokens
        sessionStorage.setItem('accessToken', responseData.access_token);
        sessionStorage.setItem('refreshToken', responseData.refresh_token);
        // Display success message
        messageElement.textContent = 'Login successful! Redirecting...';
        messageElement.style.color = 'green';

        // Wait 2 seconds before redirecting to give the user time to read the message.
        setTimeout(() => {
          loginForm.reset();
          closeModal();
          // Instead of reloading, it's often better to redirect to a dashboard or home page.
          window.location.href = 'http://127.0.0.1:8006/chat'; // Or use window.location.reload(); if you prefer.
        }, 2000); // 2000 milliseconds = 2 seconds
      } catch (error) {
        // --- Step 4: Handle any errors ---
        console.error('Login failed:', error);
        messageElement.textContent = error.message;
        messageElement.style.color = 'red';
      }
    });
  }

  if (registerForm) {
    const messageElement = registerForm.querySelector('#form-message');

    // This function now uses innerHTML to support line breaks
    const showMessage = (message, type) => {
      messageElement.innerHTML = message; // Use innerHTML
      messageElement.className = `form-message ${type}`;
    };

    registerForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      messageElement.className = 'form-message';

      const form = event.target;
      const formData = new FormData(form);
      const data = Object.fromEntries(formData.entries());

      try {
        const response = await fetch(
          'http://127.0.0.1:8002/api/v1/auth/register',
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
          }
        );

        const result = await response.json();

        if (!response.ok) {
          console.error('Server Error Details:', result); // For debugging
          const errorMessage = getErrorMessage(result);
          throw new Error(errorMessage);
        }
        console.log(result);
        showMessage(
          'Registration successful! Welcome, ' + result.name,
          'success'
        );

        setTimeout(() => {
          closeModal();
          form.reset();
          messageElement.className = 'form-message';
        }, 2000);
      } catch (error) {
        console.log(error);
        showMessage('Registration failed:<br>' + error.message, 'error');
      }
    });
  }
});

/**
 * IMPROVED helper function to extract ALL descriptive error messages
 * from a FastAPI error response.
 */
function getErrorMessage(errorData) {
  if (errorData.detail) {
    if (Array.isArray(errorData.detail)) {
      // This handles 422 validation errors
      // It maps over each error and joins them with a line break
      return errorData.detail.map((err) => err.msg).join('<br>');
    }
    // This handles custom exceptions (e.g., 409 user exists)
    return errorData.detail;
  }
  return 'An unknown error occurred.';
}
