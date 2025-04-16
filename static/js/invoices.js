// Invoices page functionality

document.addEventListener('DOMContentLoaded', function() {
  // Invoice creation functionality
  const invoiceForm = document.getElementById('invoiceForm');
  const addProductBtn = document.getElementById('addProductBtn');
  const addServiceBtn = document.getElementById('addServiceBtn');
  const invoiceItemsTable = document.getElementById('invoiceItems');
  const invoiceItemsBody = document.getElementById('invoiceItemsBody');
  const productSelect = document.getElementById('productSelect');
  const quantityInput = document.getElementById('quantityInput');
  const serviceSelect = document.getElementById('serviceSelect');
  const serviceQuantityInput = document.getElementById('serviceQuantityInput');
  const itemDiscount = document.getElementById('discount');
  const createInvoiceBtn = document.getElementById('createInvoiceBtn');
  const saveCustomerBtn = document.getElementById('saveCustomerBtn');
  const customerSelect = document.getElementById('customer_id');
  
  // Get customer button by ID instead of data attribute
  const newCustomerBtn = document.getElementById('newCustomerBtn');
  const addCustomerModal = document.getElementById('addCustomerModal');
  
  console.log('New Customer Button:', newCustomerBtn);
  console.log('Customer Modal Element:', addCustomerModal);
  
  // Check if Bootstrap is loaded (just for debugging)
  if (typeof bootstrap !== 'undefined') {
    console.log('Bootstrap is loaded');
  } else {
    console.error('Bootstrap is not loaded!');
  }
  
  // Note: Modal handling is now in create_invoice.html directly
  // We don't need to handle the modal functionality here anymore

  // Product selection functionality
  let selectedProducts = [];
  let subtotal = 0;
  let taxRate = 0.1; // 10% tax rate

  // Array to store both products and services items
  let selectedItems = [];

  // Service selection functionality
  if (serviceSelect && serviceQuantityInput && addServiceBtn) {
    // Add service to invoice
    addServiceBtn.addEventListener('click', async function() {
      const serviceId = serviceSelect.value;
      const quantity = parseInt(serviceQuantityInput.value);

      if (!serviceId || !quantity || quantity <= 0) {
        alert('Please select a service and specify a valid quantity');
        return;
      }

      try {
        const response = await fetch(`/api/service/${serviceId}`);
        const service = await response.json();

        // Check if service is already in the invoice
        const existingService = selectedItems.find(item => item.id === service.id && item.type === 'service');

        if (existingService) {
          // Update existing service quantity
          existingService.quantity += quantity;
          existingService.total = existingService.quantity * existingService.price;

          // Update the UI row
          const row = document.getElementById(`item-row-service-${service.id}`);
          if (row) {
            row.querySelector('.item-quantity').textContent = existingService.quantity;
            row.querySelector('.item-total').textContent = formatCurrency(existingService.total);
          }
        } else {
          // Add new service to the list
          const newService = {
            id: service.id,
            name: service.name,
            price: service.price,
            quantity: quantity,
            total: service.price * quantity,
            type: 'service'
          };

          selectedItems.push(newService);

          // Create new row in the table
          const newRow = document.createElement('tr');
          newRow.id = `item-row-service-${service.id}`;
          newRow.innerHTML = `
            <td>${service.name}</td>
            <td>Service</td>
            <td class="item-quantity">${quantity}</td>
            <td>${formatCurrency(service.price)}</td>
            <td class="item-total">${formatCurrency(service.price * quantity)}</td>
            <td>
              <button type="button" class="btn btn-sm btn-danger remove-item" data-id="${service.id}" data-type="service">
                <i class="bi bi-trash"></i>
              </button>
            </td>
          `;

          invoiceItemsBody.appendChild(newRow);

          // Add event listener for remove button
          newRow.querySelector('.remove-item').addEventListener('click', function() {
            const serviceId = parseInt(this.dataset.id);
            removeItem(serviceId, 'service');
          });
        }

        // Reset form
        serviceSelect.value = '';
        serviceQuantityInput.value = 1;

        // Show the table if it was hidden
        invoiceItemsTable.classList.remove('d-none');

        // Update totals
        updateTotals();

      } catch (error) {
        console.error('Error adding service to invoice:', error);
      }
    });
  }

  if (productSelect && quantityInput && addProductBtn) {
    // Get product details when a product is selected
    productSelect.addEventListener('change', async function() {
      const productId = this.value;
      if (!productId) return;

      try {
        const response = await fetch(`/api/product/${productId}`);
        const product = await response.json();

        // Update available quantity info
        const quantityInfo = document.getElementById('availableQuantity');
        if (quantityInfo) {
          quantityInfo.textContent = `Available: ${formatCurrency(product.available_quantity)}`;

          // Set max attribute on quantity input
          quantityInput.setAttribute('max', product.available_quantity);

          // Enable/disable add button based on stock
          if (product.available_quantity <= 0) {
            addProductBtn.disabled = true;
            quantityInput.disabled = true;
            quantityInfo.classList.add('text-danger');
          } else {
            addProductBtn.disabled = false;
            quantityInput.disabled = false;
            quantityInput.value = 1;
            quantityInfo.classList.remove('text-danger');
          }
        }

      } catch (error) {
        console.error('Error fetching product details:', error);
      }
    });

    // Add product to invoice
    addProductBtn.addEventListener('click', async function() {
      const productId = productSelect.value;
      const quantity = parseInt(quantityInput.value);

      if (!productId || !quantity || quantity <= 0) {
        alert('Please select a product and specify a valid quantity');
        return;
      }

      try {
        const response = await fetch(`/api/product/${productId}`);
        const product = await response.json();

        // Check if quantity is valid
        if (quantity > product.available_quantity) {
          alert(`Only ${formatCurrency(product.available_quantity)} items available in stock`);
          return;
        }

        // Check if product is already in the invoice
        const existingProduct = selectedProducts.find(p => p.id === product.id);
        if (existingProduct) {
          if (existingProduct.quantity + quantity > product.available_quantity) {
            alert(`Cannot add more. Only ${formatCurrency(product.available_quantity)} items available in stock`);
            return;
          }

          // Update existing product quantity
          existingProduct.quantity += quantity;
          existingProduct.total = existingProduct.quantity * existingProduct.price;

          // Update the UI row
          const row = document.getElementById(`item-row-${product.id}`);
          if (row) {
            row.querySelector('.item-quantity').textContent = existingProduct.quantity;
            row.querySelector('.item-total').textContent = formatCurrency(existingProduct.total);
          }
        } else {
          // Add new product to the list
          const newProduct = {
            id: product.id,
            name: product.name,
            price: product.price,
            quantity: quantity,
            total: product.price * quantity,
            type: 'product'
          };

          // Add to both arrays for compatibility during transition to using selectedItems
          selectedProducts.push(newProduct);
          selectedItems.push(newProduct);

          // Create new row in the table
          const newRow = document.createElement('tr');
          newRow.id = `item-row-product-${product.id}`;
          newRow.innerHTML = `
            <td>${product.name}</td>
            <td>Product</td>
            <td class="item-quantity">${quantity}</td>
            <td>${formatCurrency(product.price)}</td>
            <td class="item-total">${formatCurrency(product.price * quantity)}</td>
            <td>
              <button type="button" class="btn btn-sm btn-danger remove-item" data-id="${product.id}" data-type="product">
                <i class="bi bi-trash"></i>
              </button>
            </td>
          `;

          invoiceItemsBody.appendChild(newRow);

          // Add event listener for remove button
          newRow.querySelector('.remove-item').addEventListener('click', function() {
            const productId = parseInt(this.dataset.id);
            const itemType = this.dataset.type || 'product';
            removeItem(productId, itemType);
          });
        }

        // Reset form
        productSelect.value = '';
        quantityInput.value = '';
        document.getElementById('availableQuantity').textContent = '';

        // Show the table if it was hidden
        invoiceItemsTable.classList.remove('d-none');

        // Update totals
        updateTotals();

      } catch (error) {
        console.error('Error adding product to invoice:', error);
      }
    });

    // Remove item from invoice
    function removeItem(itemId, itemType = 'product') {
      // Remove from arrays
      if (itemType === 'product') {
        selectedProducts = selectedProducts.filter(p => p.id !== itemId);
      }

      selectedItems = selectedItems.filter(item => !(item.id === itemId && item.type === itemType));

      // Remove from UI
      const row = document.getElementById(`item-row-${itemType}-${itemId}`);
      if (row) {
        row.remove();
      }

      // Hide table if empty
      if (selectedItems.length === 0) {
        invoiceItemsTable.classList.add('d-none');
      }

      // Update totals
      updateTotals();
    }

    // Update invoice totals
    function updateTotals() {
      // Calculate subtotal using all items (products and services)
      subtotal = selectedItems.reduce((sum, item) => sum + item.total, 0);

      // Get discount value
      const discountValue = parseFloat(document.getElementById('discount').value) || 0;

      // Calculate tax and total
      const taxAmount = (subtotal - discountValue) * taxRate;
      const totalAmount = subtotal - discountValue + taxAmount;

      // Update UI
      document.getElementById('subtotalValue').textContent = formatCurrency(subtotal);
      document.getElementById('taxValue').textContent = formatCurrency(taxAmount);
      document.getElementById('totalValue').textContent = formatCurrency(totalAmount);
    }

    // Listen for discount changes
    if (itemDiscount) {
      itemDiscount.addEventListener('input', updateTotals);
    }

    // Create invoice submission
    if (createInvoiceBtn && invoiceForm) {
      createInvoiceBtn.addEventListener('click', async function(e) {
        e.preventDefault();

        if (selectedItems.length === 0) {
          alert('Please add at least one item (product or service) to the invoice');
          return;
        }

        // Validate form
        if (!invoiceForm.checkValidity()) {
          invoiceForm.classList.add('was-validated');
          return;
        }

        // Prepare data for submission
        const formData = new FormData(invoiceForm);
        const subtotal = parseFloat(document.getElementById('subtotalValue').textContent.replace(/[^0-9.-]+/g, ''));
        const tax = parseFloat(document.getElementById('taxValue').textContent.replace(/[^0-9.-]+/g, ''));
        const discount = parseFloat(formData.get('discount')) || 0;
        const total = parseFloat(document.getElementById('totalValue').textContent.replace(/[^0-9.-]+/g, ''));

        // Map items based on their type (products or services)
        const invoiceItems = selectedItems.map(item => {
          const baseItem = {
            quantity: item.quantity,
            unit_price: item.price,
            total_price: item.total
          };

          if (item.type === 'service') {
            return {
              ...baseItem,
              product_id: 0, // Use a dummy product ID for services
              is_service: true,
              service_id: item.id
            };
          } else {
            return {
              ...baseItem,
              product_id: item.id,
              is_service: false
            };
          }
        });

        const invoiceData = {
          customer_id: parseInt(formData.get('customer_id')),
          issue_date: formData.get('issue_date'),
          due_date: formData.get('due_date'),
          notes: formData.get('notes'),
          total_amount: subtotal,
          tax_amount: tax,
          discount: discount,
          final_amount: total,
          items: invoiceItems
        };

        try {
          // Submit the invoice
          const response = await fetch('/invoice/save', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRF-Token': document.querySelector('input[name="csrf_token"]').value
            },
            body: JSON.stringify(invoiceData)
          });
          
          const result = await response.json();
          
          // Check if response is ok (status code in 200-299 range)
          if (response.ok) {
            // Server returned a success response
            alert('Invoice created successfully');
            window.location.href = `/invoice/${result.invoice_id}`;
          } else {
            // Server returned an error response
            alert('Error creating invoice: ' + (result.message || 'Please try again'));
          }
        } catch (error) {
          console.error('Error submitting invoice:', error);
          alert('Error creating invoice. Please try again.');
        }
      });
    }
  }

  // Customer creation functionality
  if (saveCustomerBtn && customerSelect) {
    saveCustomerBtn.addEventListener('click', async function() {
      const customerForm = document.getElementById('newCustomerForm');

      // Get form values
      const name = document.getElementById('customerName').value;
      const email = document.getElementById('customerEmail').value;
      const phone = document.getElementById('customerPhone').value;
      const address = document.getElementById('customerAddress').value;
      const preferences = document.getElementById('customerPreferences').value;

      // Validate form
      if (!name) {
        document.getElementById('customerName').classList.add('is-invalid');
        return;
      } else {
        document.getElementById('customerName').classList.remove('is-invalid');
      }

      // Prepare customer data
      const customerData = {
        name: name,
        email: email || null,
        phone: phone || null,
        address: address || null,
        preferences: preferences || null
      };

      try {
        // Submit the customer
        const response = await fetch('/api/customer/create', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': document.querySelector('input[name="csrf_token"]').value
          },
          body: JSON.stringify(customerData)
        });

        const result = await response.json();

        if (result.status === 'success') {
          // Add new customer to the dropdown
          const newOption = document.createElement('option');
          newOption.value = result.customer.id;
          newOption.textContent = result.customer.name;

          // Add to dropdown and select it
          customerSelect.appendChild(newOption);
          customerSelect.value = result.customer.id;

          // Close modal using our modal manager
          console.log('Customer saved, hiding modal');
          
          if (window.modalManager && typeof window.modalManager.hide === 'function') {
            // Use our global modal manager (preferred method)
            window.modalManager.hide();
          } else {
            console.log('Modal manager not available, using fallback');
            // Fallback to manual DOM manipulation
            const modalEl = document.getElementById('addCustomerModal');
            if (modalEl) {
              // Hide modal manually
              modalEl.style.display = 'none';
              modalEl.classList.remove('show');
              document.body.classList.remove('modal-open');
              
              // Remove backdrop
              const backdrop = document.querySelector('.modal-backdrop');
              if (backdrop) {
                backdrop.remove();
              }
            }
            
            // Try clicking the close button as last resort
            const closeBtn = document.querySelector('[data-bs-dismiss="modal"]');
            if (closeBtn) {
              console.log('Clicking close button');
              closeBtn.click();
            }
          }

          // Reset form
          customerForm.reset();

          // Show success message
          alert('Customer added successfully!');
        } else {
          alert('Error creating customer: ' + result.message);
        }
      } catch (error) {
        console.error('Error creating customer:', error);
        alert('Error creating customer. Please try again.');
      }
    });
  }

  // Invoice view page functionality
  const printInvoiceBtn = document.getElementById('printInvoiceBtn');
  if (printInvoiceBtn) {
    printInvoiceBtn.addEventListener('click', function() {
      window.print();
    });
  }

  // Invoice status update buttons
  const updateStatusBtns = document.querySelectorAll('.update-status-btn');
  updateStatusBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      if (confirm(`Are you sure you want to mark this invoice as ${this.dataset.status}?`)) {
        document.getElementById(`status-form-${this.dataset.status}`).submit();
      }
    });
  });
});

function formatCurrency(amount) {
    return `₹${parseFloat(amount).toFixed(2)}`;
}