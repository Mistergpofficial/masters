 // I declare a global variable to store the last_inserted_id and visit_id
 var lastInsertedId;
 var visitId

 $(document).ready(function() {
     // Disable the button initially
     $("#ask_button").prop("disabled", true);

     // Add event listener to the input field
     $("#query_text").on("input", function() {
         var queryText = $(this).val();
         
         // Enable/disable the button based on whether there is text in the input field
         $("#ask_button").prop("disabled", !queryText.trim());
     });

     // Function to handle asking the chatbot
     function askChatbot() {
         var queryText = $("#query_text").val();

         // Disable the buttons during the request
         $("#ask_button, #download_button").prop("disabled", true);

         // Show "still thinking..." message
        $("#response").text("still thinking...");

         $.ajax({
             type: "POST",
             url: "https://cyberpro-technologies.com/ask",
             contentType: "application/json",
             data: JSON.stringify({ query_text: queryText }),
             success: function(data) {
                 $("#response").text(data.response);
                 // here i'm setting the value of the hidden input field
                 $("#last_inserted_id").val(data.last_inserted_id);
                 $("#visit_id").val(data.visit_id);
                 // we call this function in the ratings script and pass the last_inserted_id
                 updateRatings(data.last_inserted_id, data.visit_id);

                 // Show the ratings section only when a response is provided
                 if (data.response.trim() !== '') {
                     $("#rating-section").show();
                 } else {
                     // Hide the ratings section if no response is provided
                     $("#rating-section").hide();
                 }

                 // Clear the query_text input
                 $("#query_text").val('');
             },
             complete: function() {
                 // Re-enable the buttons after the request is complete
                 $("#ask_button, #download_button").prop("disabled", false);
             }
         });
         
     }

     // Add click event listener to the Ask Chatbot button
     $("#ask_button").on("click", askChatbot);

     // Function in the ratings script to update UI elements
     function updateRatings(lastInsertedId, visitId) {
         console.log("Received last_inserted_id:", lastInsertedId);
         console.log("Received visit_id:", visitId);
         $("#submit_ratings_button").prop("disabled", false);
     }



});