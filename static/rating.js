// Variable to store the timeout ID for inactivity timer
var inactivityTimer;

// Start the 5 minutes inactivity timer when the page loads
document.addEventListener('DOMContentLoaded', startInactivityTimer);

// Add event listeners for user activity
document.addEventListener('mousemove', resetInactivityTimer);
document.addEventListener('keydown', resetInactivityTimer);

// Function to start the 5 minutes inactivity timer
function startInactivityTimer() {
    inactivityTimer = setTimeout(function () {
        thirtySecondsPassed = true;
        document.getElementById('rating-section').style.display = 'none';
        document.getElementById('ease-of-use-section').style.display = 'block';

        // Alert for user awareness
        alert('5 minutes of inactivity. Showing Ease of Use section.');
    }, 5 * 60 * 1000); // 5 minutes in milliseconds
}

// Function to reset the inactivity timer upon user activity
function resetInactivityTimer() {
    clearTimeout(inactivityTimer);
    startInactivityTimer();
}

// Function to simulate submitting quality of the answer received ratings to the server
function setRating(rating, event) {
    // Retrieve the last_inserted_id from the hidden input field
    var lastInsertedId = $("#last_inserted_id").val();
    var visitId = $("#visit_id").val();

    // Setting the rating visually
    event.preventDefault();
    selectedRating = rating;
    document.querySelector('.rating').setAttribute('data-rating', rating);
    console.log("Selected Rating: ", selectedRating);

    // Submitting the rating asynchronously
    const data = {
        last_inserted_id: lastInsertedId,
        rating: rating,
        visit_id: visitId
    };

    fetch('https://msc-dissertation-fb07ddee9299.herokuapp.com/submit_rating', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Rating submitted:', data);

        // Update UI based on the response
        if (data.status === 'success') {
            alert('Rating submitted successfully!');
        } else {
            alert('Error submitting rating. Please try again.');
        }
    })
    .catch(error => {
        console.error('Error submitting rating:', error);
        alert('Error submitting rating. Please try again later.');
    });
}

// Checking if 1 minute has passed
var fiveMinutesPassed = false;

// Variable to store the timeout ID
var fiveMinutesTimer;

// Start the 5 minute timer when the page loads
document.addEventListener('DOMContentLoaded', startInactivityTimer);


// Function to reset the state for a new session
function resetSession() {
    // Reset variables and UI elements
    fiveMinutesPassed = false;
    clearTimeout(fiveMinutesTimer);
    document.getElementById('rating-section').style.display = 'none';
    document.getElementById('ease-of-use-section').style.display = 'none';

    // Start the 5 minutes timer for the new session
    startInactivityTimer();
}

// Function to set ease of use rating visually
function setEaseOfUseRating(ease_rating, event) {
    // Setting the ease of use rating visually
    event.preventDefault();
    document.querySelector('#ease-of-use-section .ease_rating').setAttribute('data-rating', ease_rating);
    console.log("Ease of Use Rating: ", ease_rating);

    // Submit the ease of use rating to the server
    submitEaseOfUseRating(ease_rating);
}

// Function to submit ease of use rating to the server
function submitEaseOfUseRating(ease_rating) {
    // Get the last_inserted_id from the hidden input field
    var lastInsertedId = $("#last_inserted_id").val();
    var visitId = $("#visit_id").val();

    // Prepare data for submission
    const data = {
        last_inserted_id: lastInsertedId,
        ease_rating: ease_rating,
        visit_id: visitId
    };

    // Submit the rating asynchronously
    fetch('https://msc-dissertation-fb07ddee9299.herokuapp.com/submit_ease_of_use_rating', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Ease of Use Rating submitted:', data);

        // Update UI based on the response
        if (data.status === 'success') {
            // Example: Update UI for success
            alert('Ease of Use Rating submitted successfully!');
            document.getElementById('ease-of-use-section').style.display = 'none';
            // Reset the session for a new session
            resetSession();
        } else {
            // Example: Update UI for other conditions
            alert('Error submitting Ease of Use Rating. Please try again.');
        }
    })
    .catch(error => {
        console.error('Error submitting Ease of Use Rating:', error);
        // Handle errors and update UI
        alert('Error submitting Ease of Use Rating. Please try again later.');
    });
}
