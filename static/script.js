// Function to fetch and display conversation history
function fetchConversationHistory() {
    $.ajax({
        type: "GET",
        url: "https://cyberpro-technologies.com/get_history",
        success: function(response) {
            var chatHistoryDiv = $('#chat-history');

            // Clear the existing content
            chatHistoryDiv.empty();

            // We check if there is conversation history
            if (response.length > 0) {
                response.forEach(function(entry) {
                    // We append the conversation history entries to the div
                    chatHistoryDiv.append(`<p>${entry.role}: ${entry.content}</p>`);
                });
                // We show the chat history div
                chatHistoryDiv.show();
            } else {
                // We hide the chat history div if there is no history
                chatHistoryDiv.hide();
            }
        },
        error: function(error) {
            console.log('Error fetching conversation history:', error);
        }
    });
}

// We execute this when the page loads
$(document).ready(function() {
    // Initially hide the chat history div
    $('#chat-history').hide();

    // We periodically update the conversation history (e.g., every 5 seconds)
    setInterval(fetchConversationHistory, 5000);
});
