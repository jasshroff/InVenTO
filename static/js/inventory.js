// Inventory page functionality

document.addEventListener('DOMContentLoaded', function() {
  // Product category filter
  const categoryFilter = document.getElementById('categoryFilter');
  if (categoryFilter) {
    categoryFilter.addEventListener('change', function() {
      const selectedCategory = this.value;
      const productRows = document.querySelectorAll('.product-row');

      productRows.forEach(row => {
        if (selectedCategory === 'all' || row.dataset.category === selectedCategory) {
          row.classList.remove('d-none');
        } else {
          row.classList.add('d-none');
        }
      });
    });
  }

  // Product search
  const productSearch = document.getElementById('productSearch');
  if (productSearch) {
    productSearch.addEventListener('input', function() {
      const searchTerm = this.value.toLowerCase().trim();
      const productRows = document.querySelectorAll('.product-row');

      productRows.forEach(row => {
        const productName = row.dataset.name.toLowerCase();
        const productBarcode = row.dataset.barcode.toLowerCase();

        if (productName.includes(searchTerm) || productBarcode.includes(searchTerm)) {
          row.classList.remove('d-none');
        } else {
          row.classList.add('d-none');
        }
      });
    });
  }

  // Stock level indicators
  const stockLevels = document.querySelectorAll('.stock-level');
  if (stockLevels.length > 0) {
    stockLevels.forEach(element => {
      const quantity = parseInt(element.dataset.quantity);

      if (quantity <= 0) {
        element.classList.add('bg-danger');
        element.textContent = 'Out of Stock';
      } else if (quantity < 10) {
        element.classList.add('bg-warning');
        element.textContent = 'Low Stock';
      } else {
        element.classList.add('bg-success');
        element.textContent = 'In Stock';
      }
    });
  }

  // Form validation for adding/editing products
  const productForm = document.getElementById('productForm');
  if (productForm) {

    productForm.addEventListener('submit', function(event) {
      if (!this.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }

      this.classList.add('was-validated');
    });
  }
});

// JavaScript for confirming delete action
function confirmDelete(message, formId) {
  if (confirm(message)) {
    document.getElementById(formId).submit();
  }
}

// Placeholder functions for editing products, categories, suppliers
function editProduct(productId) {
  // Load product data into the edit modal (you'll need to implement this)
  console.log('Editing product:', productId);
}

function editCategory(categoryId) {
  // Load category data into the edit modal (you'll need to implement this)
  console.log('Editing category:', categoryId);
}

function editSupplier(supplierId) {
  // Load supplier data into the edit modal (you'll need to implement this)
  console.log('Editing supplier:', supplierId);
}
