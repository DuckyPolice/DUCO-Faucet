// quick validation form
function formValidation() {
    var userName = document.getElementById("ducoUsername");

    if (userName && userName.value) {
        getDucos();
    } else {
        alert("Please fill your username wallet.");
    }
}

function getDucos() {
    var ducoUsername = document.getElementById("ducoUsername").value;

    fetch('https://api.stormsurge.xyz/transaction/' + ducoUsername, {
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
