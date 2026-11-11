/**
 * LANDVAULT AI — OFFICER DASHBOARD VISUALIZATIONS
 * Chart.js configurations utilizing the LandVault Heritage + Digital Intelligence palette
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Verification Status Donut Chart
  const statusCtx = document.getElementById('statusDonutChart');
  if (statusCtx) {
    new Chart(statusCtx, {
      type: 'doughnut',
      data: {
        labels: ['Verified', 'Pending Review', 'Needs Review', 'Potential Anomaly', 'Duplicate Candidates'],
        datasets: [{
          data: [980, 170, 45, 65, 35],
          backgroundColor: [
            '#16865B', // Emerald
            '#F2A93B', // Saffron
            '#4B3F72', // Midnight Violet
            '#D95C5C', // Coral Red
            '#20243A'  // Deep Indigo
          ],
          borderWidth: 2,
          borderColor: '#FFFFFF',
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              boxWidth: 12,
              padding: 14,
              font: { family: "'Inter', sans-serif", size: 11, weight: '500' }
            }
          },
          tooltip: {
            backgroundColor: '#171A3A',
            padding: 10,
            cornerRadius: 8,
            titleFont: { weight: '700' }
          }
        },
        cutout: '68%'
      }
    });
  }

  // 2. Records Processed Over Time (Line Chart)
  const timelineCtx = document.getElementById('recordsTimelineChart');
  if (timelineCtx) {
    new Chart(timelineCtx, {
      type: 'line',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct (Curr)'],
        datasets: [{
          label: 'Documents Digitized & Verified',
          data: [65, 82, 94, 110, 125, 145, 160, 185, 210, 240],
          borderColor: '#0F8B8D',
          backgroundColor: 'rgba(15, 139, 141, 0.08)',
          fill: true,
          tension: 0.35,
          borderWidth: 3,
          pointBackgroundColor: '#F2A93B',
          pointBorderColor: '#FFFFFF',
          pointBorderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#171A3A',
            padding: 10,
            cornerRadius: 8
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { font: { family: "'Inter', sans-serif", size: 11 } }
          },
          y: {
            grid: { color: 'rgba(0, 0, 0, 0.05)' },
            ticks: { font: { family: "'Inter', sans-serif", size: 11 } }
          }
        }
      }
    });
  }

  // 3. Records by District (Bar Chart)
  const districtCtx = document.getElementById('districtBarChart');
  if (districtCtx) {
    new Chart(districtCtx, {
      type: 'bar',
      data: {
        labels: ['Salem', 'Coimbatore', 'Madurai', 'Tiruchirappalli', 'Thanjavur', 'Chennai', 'Tirunelveli', 'Erode'],
        datasets: [{
          label: 'Total Land Records',
          data: [320, 245, 190, 165, 130, 95, 60, 45],
          backgroundColor: '#4B3F72',
          hoverBackgroundColor: '#0F8B8D',
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#171A3A',
            padding: 10,
            cornerRadius: 8
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { font: { family: "'Inter', sans-serif", size: 11 } }
          },
          y: {
            grid: { color: 'rgba(0, 0, 0, 0.05)' },
            ticks: { font: { family: "'Inter', sans-serif", size: 11 } }
          }
        }
      }
    });
  }
});
