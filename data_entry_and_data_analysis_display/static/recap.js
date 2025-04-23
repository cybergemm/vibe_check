$(document).ready(function() {
    // Check if we have an initial user ID
    if (initialUserId) {
        $('#recapUserId').val(initialUserId);
        loadData(initialUserId, 'weekly');
    }
    
    // Handle time period change
    $('input[name="timePeriod"]').change(function() {
        const userId = $('#recapUserId').val().trim();
        if (userId) {
            loadData(userId, $(this).val());
        }
    });
    
    // Handle form submission
    $('#userIdForm').submit(function(e) {
        e.preventDefault();
        const userId = $('#recapUserId').val().trim();
        const timePeriod = $('input[name="timePeriod"]:checked').val();
        
        if (userId) {
            loadData(userId, timePeriod);
        }
    });
    
    // Function to load data
    function loadData(userId, timePeriod) {
        // Show loading state
        $('#loading').removeClass('d-none');
        $('#weekly-recap').addClass('d-none');
        $('#monthly-recap').addClass('d-none');
        $('#no-data').addClass('d-none');
        
        // Determine the endpoint based on time period
        const endpoint = timePeriod === 'weekly' ? 'get_weekly_analysis' : 'get_monthly_analysis';
        
        // Fetch mood data
        $.ajax({
            url: `/${endpoint}/${userId}`,
            method: 'GET',
            success: function(response) {
                // Hide loading state
                $('#loading').addClass('d-none');
                
                if (!response.has_data) {
                    // Show no data message
                    $('#no-data').removeClass('d-none');
                    return;
                }
                
                // Show appropriate recap content
                if (timePeriod === 'weekly') {
                    $('#weekly-recap').removeClass('d-none');
                    updateWeeklyStats(response.analysis);
                } else {
                    $('#monthly-recap').removeClass('d-none');
                    updateMonthlyStats(response.analysis);
                }
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
    
    // Function to update weekly stats
    function updateWeeklyStats(analysis) {
        // Update most common mood
        if (analysis.most_common_mood) {
            $('#weekly-most-common-mood')
                .text(analysis.most_common_mood)
                .addClass(`mood-${analysis.most_common_mood}`);
        } else {
            $('#weekly-most-common-mood').text('No data');
        }
        
        // Update top reasons
        if (analysis.most_common_reasons && analysis.most_common_reasons.length > 0) {
            const reasonsHtml = analysis.most_common_reasons
                .map((reason, index) => `<div>${index + 1}. ${reason}</div>`)
                .join('');
            $('#weekly-top-reasons').html(reasonsHtml);
        } else {
            $('#weekly-top-reasons').text('No reasons recorded');
        }
    }
    
    // Function to update monthly stats
    function updateMonthlyStats(analysis) {
        // Group moods by day
        const moodsByDay = {};
        Object.entries(analysis.mood_patterns).forEach(([day, moods]) => {
            moods.forEach(mood => {
                if (!moodsByDay[mood]) {
                    moodsByDay[mood] = {};
                }
                moodsByDay[mood][day] = (moodsByDay[mood][day] || 0) + 1;
            });
        });
        
        // Create HTML for each mood's pattern
        const moodPatternsHtml = Object.entries(moodsByDay)
            .map(([mood, dayCounts]) => {
                // Find the day with highest count for this mood
                const mostCommonDay = Object.entries(dayCounts)
                    .sort((a, b) => b[1] - a[1])[0];
                
                // Get reasons for this mood
                const moodReasons = analysis.day_reasons[mostCommonDay[0]] || [];
                
                return `
                    <div class="mb-3">
                        <div class="mood-${mood}">
                            <strong>${mood}:</strong> Most common on ${mostCommonDay[0]} (${mostCommonDay[1]} times)
                        </div>
                        ${moodReasons.length > 0 ? 
                            `<div class="text-muted small mt-1">
                                Common reasons on ${mostCommonDay[0]}: ${moodReasons.join(', ')}
                            </div>` : 
                            ''
                        }
                    </div>
                `;
            })
            .join('');
        
        $('#monthly-mood-patterns').html(moodPatternsHtml);
    }
}); 
