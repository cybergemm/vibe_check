$(document).ready(function() {
    // Initialize variables
    // Removed chart variables
    
    // Check if we have an initial user ID
    if (initialUserId) {
        $('#recapUserId').val(initialUserId);
        loadWeeklyData(initialUserId);
    }
    
    // Handle form submission
    $('#userIdForm').submit(function(e) {
        e.preventDefault();
        const userId = $('#recapUserId').val().trim();
        
        if (userId) {
            loadWeeklyData(userId);
        }
    });
    
    // Function to load weekly data
    function loadWeeklyData(userId) {
        // Show loading state
        $('#loading').removeClass('d-none');
        $('#recap-content').addClass('d-none');
        $('#no-data').addClass('d-none');
        
        // Removed chart destruction code
        
        // Fetch weekly mood data
        $.ajax({
            url: `/get_weekly_analysis/${userId}`,
            method: 'GET',
            success: function(response) {
                // Hide loading state
                $('#loading').addClass('d-none');
                
                if (!response.has_data) {
                    // Show no data message
                    $('#no-data').removeClass('d-none');
                    return;
                }
                
                // Show recap content
                $('#recap-content').removeClass('d-none');
                
                // Update stats
                updateStats(response.analysis);
                
                // Removed chart creation code
            },
            error: function() {
                // Hide loading state
                $('#loading').addClass('d-none');
                
                // Show error message
                $('#no-data').removeClass('d-none').find('.alert')
                    .removeClass('alert-info')
                    .addClass('alert-danger')
                    .find('h4').text('Error loading data');
            }
        });
    }
    
    // Function to update stats
    function updateStats(analysis) {
        // Update best and worst days
        $('#best-day').text(analysis.best_day || 'No data');
        $('#worst-day').text(analysis.worst_day || 'No data');
        
        // Update most common mood
        if (analysis.most_common_mood) {
            $('#most-common-mood')
                .text(analysis.most_common_mood)
                .addClass(`mood-${analysis.most_common_mood}`);
        } else {
            $('#most-common-mood').text('No data');
        }
        
        // Update top reasons
        if (analysis.most_common_reasons && analysis.most_common_reasons.length > 0) {
            const reasonsHtml = analysis.most_common_reasons
                .map((reason, index) => `<div>${index + 1}. ${reason}</div>`)
                .join('');
            $('#top-reasons').html(reasonsHtml);
        } else {
            $('#top-reasons').text('No reasons recorded');
        }
    }
    
    // Removed chart creation functions
}); 
