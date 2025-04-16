// Dashboard charts and functionality

document.addEventListener('DOMContentLoaded', function() {
  // Sales chart for the dashboard
  const salesChartElem = document.getElementById('salesChart');
  if (salesChartElem) {
    const salesData = JSON.parse(salesChartElem.dataset.sales || '[]');
    
    if (salesData.length > 0) {
      const labels = salesData.map(item => {
        const date = new Date(item.date);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      });
      
      const data = salesData.map(item => item.amount);
      
      const ctx = salesChartElem.getContext('2d');
      new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: 'Daily Sales',
            data: data,
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 2,
            tension: 0.4,
            fill: true
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  return '₹' + context.raw.toLocaleString('en-IN');
                }
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                callback: function(value) {
                  return '₹' + value.toLocaleString('en-IN');
                }
              }
            }
          }
        }
      });
    } else {
      salesChartElem.parentElement.innerHTML = '<div class="alert alert-info">No sales data available</div>';
    }
  }
  
  // Top products chart
  const topProductsChartElem = document.getElementById('topProductsChart');
  if (topProductsChartElem) {
    const productsData = topProductsChartElem.dataset.products;
    if (productsData) {
      const data = JSON.parse(productsData);
      const labels = data.map(item => item[0]); // Product names
      const quantities = data.map(item => item[1]); // Quantities
      
      const ctx = topProductsChartElem.getContext('2d');
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Units Sold',
            data: quantities,
            backgroundColor: [
              'rgba(255, 99, 132, 0.5)',
              'rgba(54, 162, 235, 0.5)',
              'rgba(255, 206, 86, 0.5)',
              'rgba(75, 192, 192, 0.5)',
              'rgba(153, 102, 255, 0.5)'
            ],
            borderColor: [
              'rgba(255, 99, 132, 1)',
              'rgba(54, 162, 235, 1)',
              'rgba(255, 206, 86, 1)',
              'rgba(75, 192, 192, 1)',
              'rgba(153, 102, 255, 1)'
            ],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                precision: 0
              }
            }
          }
        }
      });
    } else {
      topProductsChartElem.parentElement.innerHTML = '<div class="alert alert-info">No product data available</div>';
    }
  }
});
