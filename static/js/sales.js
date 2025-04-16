// Sales page functionality

document.addEventListener('DOMContentLoaded', function() {
  // Date range filter for sales
  const startDateFilter = document.getElementById('startDateFilter');
  const endDateFilter = document.getElementById('endDateFilter');
  const applyDateFilter = document.getElementById('applyDateFilter');
  
  if (startDateFilter && endDateFilter && applyDateFilter) {
    applyDateFilter.addEventListener('click', function() {
      const startDate = startDateFilter.value ? new Date(startDateFilter.value) : null;
      const endDate = endDateFilter.value ? new Date(endDateFilter.value) : null;
      
      const invoiceRows = document.querySelectorAll('.invoice-row');
      
      invoiceRows.forEach(row => {
        const invoiceDate = new Date(row.dataset.date);
        let showRow = true;
        
        if (startDate && invoiceDate < startDate) {
          showRow = false;
        }
        
        if (endDate && invoiceDate > endDate) {
          showRow = false;
        }
        
        if (showRow) {
          row.classList.remove('d-none');
        } else {
          row.classList.add('d-none');
        }
      });
    });
  }
  
  // Status filter for sales
  const statusFilter = document.getElementById('statusFilter');
  if (statusFilter) {
    statusFilter.addEventListener('change', function() {
      const selectedStatus = this.value;
      const invoiceRows = document.querySelectorAll('.invoice-row');
      
      invoiceRows.forEach(row => {
        if (selectedStatus === 'all' || row.dataset.status === selectedStatus) {
          row.classList.remove('d-none');
        } else {
          row.classList.add('d-none');
        }
      });
    });
  }
  
  // Totals calculation
  function updateSalesTotal() {
    const visibleRows = document.querySelectorAll('.invoice-row:not(.d-none)');
    const totalElement = document.getElementById('totalSales');
    
    if (totalElement) {
      let total = 0;
      
      visibleRows.forEach(row => {
        if (row.dataset.status === 'paid') {
          total += parseFloat(row.dataset.amount);
        }
      });
      
      totalElement.textContent = formatCurrency(total);
    }
  }
  
  // Update totals when filters change
  if (statusFilter) {
    statusFilter.addEventListener('change', updateSalesTotal);
  }
  
  if (applyDateFilter) {
    applyDateFilter.addEventListener('click', updateSalesTotal);
  }
  
  // Initial calculation
  updateSalesTotal();
});
