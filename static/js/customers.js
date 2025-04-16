// Customers page functionality

document.addEventListener('DOMContentLoaded', function() {
  // Customer search functionality
  const customerSearch = document.getElementById('customerSearch');
  if (customerSearch) {
    customerSearch.addEventListener('input', function() {
      const searchTerm = this.value.toLowerCase().trim();
      const customerRows = document.querySelectorAll('.customer-row');
      
      customerRows.forEach(row => {
        const customerName = row.dataset.name.toLowerCase();
        const customerEmail = (row.dataset.email || '').toLowerCase();
        const customerPhone = (row.dataset.phone || '').toLowerCase();
        
        if (customerName.includes(searchTerm) || 
            customerEmail.includes(searchTerm) || 
            customerPhone.includes(searchTerm)) {
          row.classList.remove('d-none');
        } else {
          row.classList.add('d-none');
        }
      });
    });
  }
  
  // Form validation for adding/editing customers
  const customerForm = document.getElementById('customerForm');
  if (customerForm) {
    customerForm.addEventListener('submit', function(event) {
      if (!this.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      
      this.classList.add('was-validated');
    });
  }
  
  // Customer detail view toggle
  const customerDetailButtons = document.querySelectorAll('.view-customer-details');
  if (customerDetailButtons.length > 0) {
    customerDetailButtons.forEach(button => {
      button.addEventListener('click', function() {
        const customerId = this.dataset.id;
        const detailsRow = document.getElementById(`customer-details-₹{customerId}`);
        
        if (detailsRow) {
          if (detailsRow.classList.contains('d-none')) {
            // Hide all other details first
            document.querySelectorAll('.customer-details-row').forEach(row => {
              row.classList.add('d-none');
            });
            
            // Show this one
            detailsRow.classList.remove('d-none');
            this.innerHTML = '<i class="bi bi-chevron-up"></i> Hide Details';
          } else {
            detailsRow.classList.add('d-none');
            this.innerHTML = '<i class="bi bi-chevron-down"></i> View Details';
          }
        }
      });
    });
  }
});
