$(document).ready(function() {
    let selectedMood = null;
    const form = $('#moodForm');
    const userIdInput = $('#userId');
    const moodInput = $('#selectedMood');
    const moodButtons = $('.btn-mood');

    // Handle mood button clicks
    moodButtons.click(function() {
        moodButtons.removeClass('selected');
        $(this).addClass('selected');
        selectedMood = $(this).data('mood');
        moodInput.val(selectedMood);
        
        // Clear any validation errors for mood selection
        moodInput.removeClass('is-invalid');
    });

    // Handle form submission
    form.submit(function(e) {
        e.preventDefault();
        
        // Reset validation state
        userIdInput.removeClass('is-invalid');
        moodInput.removeClass('is-invalid');
        
        let isValid = true;
        const userId = userIdInput.val().trim();
        
        // Validate user ID
        if (!userId) {
            userIdInput.addClass('is-invalid');
            isValid = false;
        }
        
        // Validate mood selection
        if (!selectedMood) {
            moodInput.addClass('is-invalid');
            isValid = false;
        }
        
        // If form is not valid, stop submission
        if (!isValid) {
            showMessage('Please fill in all required fields', 'error');
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
                form[0].reset();
                moodButtons.removeClass('selected');
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
