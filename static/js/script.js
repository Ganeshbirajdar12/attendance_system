// Attendance Chart Script
const ctx = document.getElementById('attendanceChart').getContext('2d');

const attendanceChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['DBMS', 'DSA', 'Python', 'Maths'],
        datasets: [{
            label: 'Attendance %',
            data: [92, 78, 100, 65],
            backgroundColor: [
                'rgba(76, 175, 80, 0.7)',
                'rgba(255, 152, 0, 0.7)',
                'rgba(33, 150, 243, 0.7)',
                'rgba(244, 67, 54, 0.7)'
            ],
            borderColor: [
                'rgba(76, 175, 80, 1)',
                'rgba(255, 152, 0, 1)',
                'rgba(33, 150, 243, 1)',
                'rgba(244, 67, 54, 1)'
            ],
            borderWidth: 2,
            borderRadius: 6
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true,
                max: 100
            }
        },
        plugins: {
            legend: {
                display: false
            }
        }
    }
});
