// Function to fetch and display conversation history
function fetchConversationHistory() {
    $.ajax({
        type: "GET",
        url: "https://cyberpro-technologies.com/get_history",
        success: function(response) {
            var chatHistoryDiv = $('#chat-history');
            var heading = $('#conversation-heading');

            // Clear the existing content
            chatHistoryDiv.empty();

            // We check if there is conversation history
            if (response.length > 0) {
                response.forEach(function(entry) {
                    // We append the conversation history entries to the div
                    chatHistoryDiv.append(`<p>${entry.role}: ${entry.content}</p>`);
                });
                // We show the chat history div and the heading
                chatHistoryDiv.show();
                heading.show();
            } else {
                // We hide the chat history div and the heading if there is no history
                chatHistoryDiv.hide();
                heading.hide();
            }
        },
        error: function(error) {
            console.log('Error fetching conversation history:', error);
        }
    });
}

// We execute this when the page loads
$(document).ready(function() {
    // Initially hide the chat history div and the heading
    $('#chat-history, #conversation-heading').hide();

    // Add the conversation history heading
    $('body').prepend('<h1 id="conversation-heading">Conversation History</h1>');

    // We periodically update the conversation history (e.g., every 5 seconds)
    setInterval(fetchConversationHistory, 5000);
});
