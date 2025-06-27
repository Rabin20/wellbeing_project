document.addEventListener('DOMContentLoaded', function() {
    // Initialize any dashboard-specific JS
    console.log('Dashboard loaded');
    
    // Initialize charts
    if (document.getElementById('moodChart')) {
        initMoodChart();
    }
});

function initMoodChart() {
    // Chart.js implementation for mood tracking
    const ctx = document.getElementById('moodChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Mood Level',
                data: [3, 4, 4, 5, 3, 2, 4],
                backgroundColor: 'rgba(78, 115, 223, 0.05)',
                borderColor: 'rgba(78, 115, 223, 1)',
                pointBackgroundColor: 'rgba(78, 115, 223, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(78, 115, 223, 1)',
                pointRadius: 3,
                pointHoverRadius: 5,
                tension: 0.3
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: false,
                    min: 0,
                    max: 5,
                    ticks: {
                        callback: function(value) {
                            const moods = ['', 'Angry', 'Sad', 'Neutral', 'Calm', 'Happy'];
                            return moods[value] || '';
                        }
                    }
                }
            }
        }
    });
}