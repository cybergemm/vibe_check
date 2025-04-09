$(document).ready(function() {
    let selectedMood = null;

    // Handle mood button clicks
    $('.btn-mood').click(function() {
        $('.btn-mood').removeClass('selected');
        $(this).addClass('selected');
        selectedMood = $(this).data('mood');
    });

    // Handle form submission
    $('#moodForm').submit(function(e) {
        e.preventDefault();
        
        const userId = $('#userId').val().trim();
        
        if (!userId) {
            showMessage('Please enter your unique identifier', 'error');
            return;
        }
        
        if (!selectedMood) {
            showMessage('Please select your mood', 'error');
            return;
        }

        // Submit the mood entry
        $.ajax({
            url: '/submit_mood',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                user_id: userId,
                mood: selectedMood
            }),
            success: function(response) {
                showMessage('Mood recorded successfully!', 'success');
                // Reset the form
                $('#userId').val('');
                $('.btn-mood').removeClass('selected');
                selectedMood = null;
            },
            error: function(xhr) {
                showMessage('Error recording mood. Please try again.', 'error');
            }
        });
    });

    function showMessage(message, type) {
        const messageDiv = $('#message');
        messageDiv.text(message)
            .removeClass('success error')
            .addClass(type);
        
        // Clear the message after 3 seconds
        setTimeout(() => {
            messageDiv.text('').removeClass('success error');
        }, 3000);
    }
}); 
