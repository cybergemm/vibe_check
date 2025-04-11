$(document).ready(function() {
    let selectedMood = null;
    const form = $('#moodForm');
    const userIdInput = $('#userId');
    const moodInput = $('#selectedMood');
    const moodButtons = $('.btn-mood');
    const messageDiv = $('#message');
    const submitButton = $('button[type="submit"]');

    // Handle mood button clicks
    moodButtons.click(function() {
        moodButtons.removeClass('selected');
        $(this).addClass('selected');
        selectedMood = $(this).data('mood');
        moodInput.val(selectedMood);
        
        // Clear any validation errors for mood selection
        moodInput.removeClass('is-invalid');
    });

    // Check for existing entry when user ID changes
    let checkTimeout;
    userIdInput.on('input', function() {
        const userId = $(this).val().trim();
        
        // Clear previous timeout
        clearTimeout(checkTimeout);
        
        // If user ID is empty, reset form state
        if (!userId) {
            submitButton.prop('disabled', false);
            moodButtons.prop('disabled', false);
            return;
        }
        
        // Set a timeout to avoid too many requests while typing
        checkTimeout = setTimeout(function() {
            // Disable form while checking
            submitButton.prop('disabled', true);
            moodButtons.prop('disabled', true);
            
            $.ajax({
                url: `/check_today_entry/${userId}`,
                method: 'GET',
                success: function(response) {
                    if (response.has_entry) {
                        showMessage("You've already tracked today's mood!", 'info');
                        
                        // Disable form submission
                        submitButton.prop('disabled', true);
                        moodButtons.prop('disabled', true);
                    } else {
                        // Enable form submission
                        submitButton.prop('disabled', false);
                        moodButtons.prop('disabled', false);
                    }
                },
                error: function() {
                    // On error, enable form submission
                    submitButton.prop('disabled', false);
                    moodButtons.prop('disabled', false);
                }
            });
        }, 500); // Wait 500ms after user stops typing
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
                
                // Disable form after successful submission
                submitButton.prop('disabled', true);
                moodButtons.prop('disabled', true);
            },
            error: function(xhr) {
                // Check if there's a specific error message from the server
                if (xhr.status === 409) {
                    showMessage("You've already tracked today's mood!", 'error');
                } else {
                    showMessage('Error recording mood. Please try again.', 'error');
                }
            }
        });
    });

    function showMessage(message, type) {
        messageDiv.text(message)
            .removeClass('success error info')
            .addClass(type);
        
        // Clear the message after appropriate timeout
        let timeout;
        switch(type) {
            case 'error':
                timeout = 5000; // 5 seconds for errors
                break;
            case 'info':
                timeout = 4000; // 4 seconds for info
                break;
            default:
                timeout = 3000; // 3 seconds for success
        }
        
        setTimeout(() => {
            messageDiv.text('').removeClass('success error info');
        }, timeout);
    }
}); 
