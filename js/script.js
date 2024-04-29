// ReCAPTCHA v3 site key
const SITE_KEY = 'sussy_dude_edit_this';

// Function to execute reCAPTCHA and submit form
function executeRecaptchaAndSubmit() {
    grecaptcha.ready(function() {
        grecaptcha.execute(SITE_KEY, { action: 'submit' }).then(function(token) {
            document.getElementById('recaptchaToken').value = token;
            document.getElementById('ducoForm').submit(); // Submit the form
        });
    });
}

// Modify form validation function
function formValidation() {
    executeRecaptchaAndSubmit();
}

// Update getDucos() function to include the reCAPTCHA token in the request
function getDucos() {
    var ducoUsername = document.getElementById("ducoUsername").value;
    var recaptchaToken = document.getElementById("recaptchaToken").value;

    // Include recaptchaToken in the request
    fetch('https://127.0.0.1:7457/transaction/' + ducoUsername + '?recaptchaToken=' + recaptchaToken, {
        method: 'GET'
    })
    .then(response => {
        if (response.status != 404) {
            return response.text(); // Return the text promise
        } else {
            console.error('Network response was not ok');
            return Promise.reject('Network response was not ok');
        }
    })
    .then(text => {
        alert(text); // Handle the text content here
        // Add other logic as needed
    })
    .catch(error => {
        console.error('Error:', error);
        location.reload();
    });
}
