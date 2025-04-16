// Reports page functionality

document.addEventListener('DOMContentLoaded', function() {
  // Report type selection
  const reportTypeSelect = document.getElementById('report_type');
  const dateFields = document.getElementById('dateFields');
  
  if (reportTypeSelect && dateFields) {
    reportTypeSelect.addEventListener('change', function() {
      const reportType = this.value;
      
      // Show/hide date fields based on report type
      if (reportType === 'inventory') {
        dateFields.classList.add('d-none');
      } else {
        dateFields.classList.remove('d-none');
      }
    });
  }
  
  // Sales report chart
  const salesReportChart = document.getElementById('salesReportChart');
  if (salesReportChart) {
    const chartData = salesReportChart.dataset.report;
    
    if (chartData) {
      const reportData = JSON.parse(chartData);
      const labels = reportData.map(item => formatDate(item[0]));
      const values = reportData.map(item => parseFloat(item[1]));
      
      const ctx = salesReportChart.getContext('2d');
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Sales Amount',
            data: values,
            backgroundColor: 'rgba(54, 162, 235, 0.5)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                callback: function(value) {
                  return '₹' + value;
                }
              }
            }
          },
          plugins: {
            tooltip: {
              callbacks: {
                label: function(context) {
                  return formatCurrency(context.raw);
                }
              }
            }
          }
        }
      });
    }
  }
  
  // Export report functionality
  const exportReportBtn = document.getElementById('exportReportBtn');
  if (exportReportBtn) {
    exportReportBtn.addEventListener('click', function() {
      const reportTable = document.getElementById('reportTable');
      if (!reportTable) return;
      
      // Get table data
      const headers = [];
      const data = [];
      
      // Get headers
      reportTable.querySelectorAll('thead th').forEach(th => {
        headers.push(th.textContent);
      });
      
      // Get rows
      reportTable.querySelectorAll('tbody tr').forEach(tr => {
        const rowData = [];
        tr.querySelectorAll('td').forEach(td => {
          rowData.push(td.textContent);
        });
        data.push(rowData);
      });
      
      // Prepare CSV content
      let csvContent = headers.join(',') + '\n';
      data.forEach(row => {
        csvContent += row.join(',') + '\n';
      });
      
      // Create download link
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', 'report.csv');
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    });
  }
});

// Helper function to format date
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString();
}
