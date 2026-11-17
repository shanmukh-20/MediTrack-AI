/**
 * MediTrack AI - Analytics Charts Initialization
 * Uses standard Chart.js with clean medical palette and readable labels.
 */

function initAnalyticsCharts(chartData) {
  if (!chartData || typeof Chart === 'undefined') {
    return;
  }

  // 1. Adherence Doughnut Chart
  const adherenceCtx = document.getElementById('adherenceChart');
  if (adherenceCtx && chartData.adherence) {
    const taken = chartData.adherence.taken || 0;
    const missed = chartData.adherence.missed || 0;
    const total = taken + missed;

    new Chart(adherenceCtx, {
      type: 'doughnut',
      data: {
        labels: ['Taken Doses', 'Missed Doses'],
        datasets: [{
          data: total > 0 ? [taken, missed] : [0, 0],
          backgroundColor: ['#16a34a', '#dc2626'],
          borderColor: '#ffffff',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { boxWidth: 12, padding: 15, font: { size: 12 } }
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                const val = context.raw || 0;
                const pct = total > 0 ? Math.round((val / total) * 100) : 0;
                return ` ${context.label}: ${val} (${pct}%)`;
              }
            }
          }
        },
        cutout: '68%'
      }
    });
  }

  // 2. Doses by Medicine Bar Chart
  const medicineCtx = document.getElementById('medicineDosesChart');
  if (medicineCtx && chartData.medicine_doses) {
    new Chart(medicineCtx, {
      type: 'bar',
      data: {
        labels: chartData.medicine_doses.labels,
        datasets: [{
          label: 'Taken Doses',
          data: chartData.medicine_doses.values,
          backgroundColor: '#1d4ed8',
          borderRadius: 3,
          maxBarThickness: 32
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { precision: 0, font: { size: 11 } },
            grid: { color: '#f1f5f9' }
          },
          x: {
            grid: { display: false },
            ticks: { font: { size: 11 } }
          }
        }
      }
    });
  }

  // 3. Daily Activity Line Chart (Last 7 Days)
  const activityCtx = document.getElementById('dailyActivityChart');
  if (activityCtx && chartData.daily_activity) {
    new Chart(activityCtx, {
      type: 'line',
      data: {
        labels: chartData.daily_activity.labels,
        datasets: [{
          label: 'Doses Taken',
          data: chartData.daily_activity.values,
          borderColor: '#0284c7',
          backgroundColor: 'rgba(2, 132, 199, 0.08)',
          borderWidth: 2,
          fill: true,
          tension: 0.25,
          pointRadius: 4,
          pointBackgroundColor: '#0284c7'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { precision: 0, font: { size: 11 } },
            grid: { color: '#f1f5f9' }
          },
          x: {
            grid: { display: false },
            ticks: { font: { size: 11 } }
          }
        }
      }
    });
  }
}
