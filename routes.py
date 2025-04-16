import os
import logging
from datetime import datetime, timedelta
from decimal import Decimal
import json

from flask import render_template, url_for, flash, redirect, request, jsonify, abort, make_response
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash
from sqlalchemy import func, desc

from app import app, db
from models import User, Category, Supplier, Product, Customer, Invoice, InvoiceItem, JewelryService
from forms import (RegistrationForm, LoginForm, CategoryForm, SupplierForm, ProductForm, 
                  CustomerForm, InvoiceForm, InvoiceItemForm, JewelryServiceForm, ReportForm)
from utils import generate_invoice_number, generate_invoice_pdf

# Set up logging
logger = logging.getLogger(__name__)

# Home route
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Your account has been created! You can now log in', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('You have been logged in!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    
    return render_template('login.html', title='Login', form=form)

# User Logout
@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    # Get recent sales data (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Total sales
    total_sales = db.session.query(func.sum(Invoice.final_amount))\
        .filter(Invoice.status == 'paid', Invoice.issue_date >= thirty_days_ago).scalar() or 0
    
    # Total products
    total_products = Product.query.count()
    
    # Low stock products (less than 10 items)
    low_stock_count = Product.query.filter(Product.quantity < 10).count()
    
    # Recent invoices
    recent_invoices = Invoice.query.order_by(desc(Invoice.created_at)).limit(5).all()
    
    # Sales data for the chart (last 7 days)
    sales_data = []
    for i in range(7, 0, -1):
        date = datetime.utcnow() - timedelta(days=i-1)
        daily_sales = db.session.query(func.sum(Invoice.final_amount))\
            .filter(Invoice.status == 'paid',
                    func.date(Invoice.issue_date) == func.date(date)).scalar() or 0
        sales_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'amount': float(daily_sales)
        })
    
    # Top selling products
    top_products = db.session.query(
        Product.name,
        func.sum(InvoiceItem.quantity).label('total_quantity')
    ).join(InvoiceItem).join(Invoice).filter(
        Invoice.status == 'paid',
        Invoice.issue_date >= thirty_days_ago
    ).group_by(Product.id).order_by(desc('total_quantity')).limit(5).all()
    
    return render_template('dashboard.html', 
                          title='Dashboard',
                          total_sales=total_sales,
                          total_products=total_products,
                          low_stock_count=low_stock_count,
                          recent_invoices=recent_invoices,
                          sales_data=json.dumps(sales_data),
                          top_products=top_products)

# Inventory Routes
@app.route('/inventory')
@login_required
def inventory():
    products = Product.query.all()
    categories = Category.query.all()
    suppliers = Supplier.query.all()
    return render_template('inventory.html', 
                          title='Inventory Management',
                          products=products,
                          categories=categories,
                          suppliers=suppliers)

# Category Routes
@app.route('/category/new', methods=['GET', 'POST'])
@login_required
def new_category():
    form = CategoryForm()
    form.original_name = None
    
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(category)
        db.session.commit()
        flash('Category has been created!', 'success')
        return redirect(url_for('inventory'))
    
    return render_template('inventory.html', 
                          title='New Category',
                          form=form, 
                          category_form=True)

@app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    form = CategoryForm()
    form.original_name = category.name
    
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        db.session.commit()
        flash('Category has been updated!', 'success')
        return redirect(url_for('inventory'))
    
    if request.method == 'GET':
        form.name.data = category.name
        form.description.data = category.description
    
    return render_template('inventory.html', 
                          title='Edit Category',
                          form=form, 
                          category_form=True)

@app.route('/category/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    
    # Check if there are products in this category
    if category.products:
        flash('Cannot delete category with associated products!', 'danger')
        return redirect(url_for('inventory'))
    
    db.session.delete(category)
    db.session.commit()
    flash('Category has been deleted!', 'success')
    return redirect(url_for('inventory'))

# Supplier Routes
@app.route('/supplier/new', methods=['GET', 'POST'])
@login_required
def new_supplier():
    form = SupplierForm()
    
    if form.validate_on_submit():
        supplier = Supplier(
            name=form.name.data,
            contact_person=form.contact_person.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data
        )
        db.session.add(supplier)
        db.session.commit()
        flash('Supplier has been created!', 'success')
        return redirect(url_for('inventory'))
    
    return render_template('inventory.html', 
                          title='New Supplier',
                          form=form, 
                          supplier_form=True)

@app.route('/supplier/<int:supplier_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    form = SupplierForm()
    
    if form.validate_on_submit():
        supplier.name = form.name.data
        supplier.contact_person = form.contact_person.data
        supplier.email = form.email.data
        supplier.phone = form.phone.data
        supplier.address = form.address.data
        db.session.commit()
        flash('Supplier has been updated!', 'success')
        return redirect(url_for('inventory'))
    
    if request.method == 'GET':
        form.name.data = supplier.name
        form.contact_person.data = supplier.contact_person
        form.email.data = supplier.email
        form.phone.data = supplier.phone
        form.address.data = supplier.address
    
    return render_template('inventory.html', 
                          title='Edit Supplier',
                          form=form, 
                          supplier_form=True)

@app.route('/supplier/<int:supplier_id>/delete', methods=['POST'])
@login_required
def delete_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    
    # Check if there are products with this supplier
    if supplier.products:
        flash('Cannot delete supplier with associated products!', 'danger')
        return redirect(url_for('inventory'))
    
    db.session.delete(supplier)
    db.session.commit()
    flash('Supplier has been deleted!', 'success')
    return redirect(url_for('inventory'))

# Product Routes
@app.route('/product/new', methods=['GET', 'POST'])
@login_required
def new_product():
    form = ProductForm()
    form.original_barcode = None
    
    # Get categories and suppliers for dropdowns
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    form.supplier_id.choices = [(s.id, s.name) for s in Supplier.query.all()]
    
    # Generate a new unique 5-digit barcode
    if request.method == 'GET':
        # Find the highest existing barcode and increment by 1
        last_product = Product.query.order_by(Product.id.desc()).first()
        if last_product and last_product.barcode and last_product.barcode.isdigit():
            # If the last barcode exists and is a number, increment it
            new_barcode = str(int(last_product.barcode) + 1).zfill(5)
        else:
            # Start with 10000 if no products exist or last product has no valid barcode
            new_barcode = '10000'
        
        # Ensure the barcode is unique
        while Product.query.filter_by(barcode=new_barcode).first():
            # If the barcode already exists, increment by 1
            new_barcode = str(int(new_barcode) + 1).zfill(5)
        
        form.barcode.data = new_barcode
    
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            barcode=form.barcode.data,
            price=form.price.data,
            cost_price=form.cost_price.data,
            quantity=form.quantity.data,
            
            # Jewelry-specific attributes
            material=form.material.data,
            metal_type=form.metal_type.data,
            purity=form.purity.data,
            stone_type=form.stone_type.data,
            stone_count=form.stone_count.data,
            stone_carat=form.stone_carat.data,
            weight=form.weight.data,
            size=form.size.data,
            
            category_id=form.category_id.data,
            supplier_id=form.supplier_id.data
        )
        db.session.add(product)
        db.session.commit()
        flash('Product has been created!', 'success')
        return redirect(url_for('inventory'))
    
    return render_template('inventory.html', 
                          title='New Product',
                          form=form, 
                          product_form=True)

@app.route('/product/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm()
    form.original_barcode = product.barcode
    
    # Get categories and suppliers for dropdowns
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    form.supplier_id.choices = [(s.id, s.name) for s in Supplier.query.all()]
    
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.barcode = form.barcode.data
        product.price = form.price.data
        product.cost_price = form.cost_price.data
        product.quantity = form.quantity.data
        
        # Jewelry-specific attributes
        product.material = form.material.data
        product.metal_type = form.metal_type.data
        product.purity = form.purity.data
        product.stone_type = form.stone_type.data
        product.stone_count = form.stone_count.data
        product.stone_carat = form.stone_carat.data
        product.weight = form.weight.data
        product.size = form.size.data
        
        product.category_id = form.category_id.data
        product.supplier_id = form.supplier_id.data
        product.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Product has been updated!', 'success')
        return redirect(url_for('inventory'))
    
    if request.method == 'GET':
        form.name.data = product.name
        form.description.data = product.description
        form.barcode.data = product.barcode
        form.price.data = product.price
        form.cost_price.data = product.cost_price
        form.quantity.data = product.quantity
        
        # Jewelry-specific attributes
        form.material.data = product.material
        form.metal_type.data = product.metal_type
        form.purity.data = product.purity
        form.stone_type.data = product.stone_type
        form.stone_count.data = product.stone_count
        form.stone_carat.data = product.stone_carat
        form.weight.data = product.weight
        form.size.data = product.size
        
        form.category_id.data = product.category_id
        form.supplier_id.data = product.supplier_id
    
    return render_template('inventory.html', 
                          title='Edit Product',
                          form=form, 
                          product_form=True)

@app.route('/product/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Check if product is used in invoices
    if product.invoice_items:
        flash('Cannot delete product that has been sold!', 'danger')
        return redirect(url_for('inventory'))
    
    db.session.delete(product)
    db.session.commit()
    flash('Product has been deleted!', 'success')
    return redirect(url_for('inventory'))

# Customer Routes
@app.route('/customers')
@login_required
def customers():
    form = CustomerForm()
    all_customers = Customer.query.all()
    return render_template('customers.html', 
                          title='Customer Management',
                          customers=all_customers,
                          form=form)

@app.route('/customer/new', methods=['GET', 'POST'])
@login_required
def new_customer():
    form = CustomerForm()
    
    if form.validate_on_submit():
        customer = Customer(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            
            # Jewelry store customer-specific information
            birthdate=form.birthdate.data,
            anniversary=form.anniversary.data,
            preferences=form.preferences.data,
            ring_size=form.ring_size.data,
            bracelet_size=form.bracelet_size.data,
            necklace_length=form.necklace_length.data
        )
        db.session.add(customer)
        db.session.commit()
        flash('Customer has been created!', 'success')
        return redirect(url_for('customers'))
    
    return render_template('customers.html', 
                          title='New Customer',
                          form=form, 
                          customer_form=True)

@app.route('/customer/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    form = CustomerForm()
    
    if form.validate_on_submit():
        customer.name = form.name.data
        customer.email = form.email.data
        customer.phone = form.phone.data
        customer.address = form.address.data
        
        # Jewelry store customer-specific information
        customer.birthdate = form.birthdate.data
        customer.anniversary = form.anniversary.data
        customer.preferences = form.preferences.data
        customer.ring_size = form.ring_size.data
        customer.bracelet_size = form.bracelet_size.data
        customer.necklace_length = form.necklace_length.data
        db.session.commit()
        flash('Customer has been updated!', 'success')
        return redirect(url_for('customers'))
    
    if request.method == 'GET':
        form.name.data = customer.name
        form.email.data = customer.email
        form.phone.data = customer.phone
        form.address.data = customer.address
        
        # Jewelry store customer-specific information
        form.birthdate.data = customer.birthdate
        form.anniversary.data = customer.anniversary
        form.preferences.data = customer.preferences
        form.ring_size.data = customer.ring_size
        form.bracelet_size.data = customer.bracelet_size
        form.necklace_length.data = customer.necklace_length
    
    return render_template('customers.html', 
                          title='Edit Customer',
                          form=form, 
                          customer_form=True)

@app.route('/customer/<int:customer_id>/delete', methods=['POST'])
@login_required
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    
    # Check if customer has invoices
    if customer.invoices:
        flash('Cannot delete customer with associated invoices!', 'danger')
        return redirect(url_for('customers'))
    
    db.session.delete(customer)
    db.session.commit()
    flash('Customer has been deleted!', 'success')
    return redirect(url_for('customers'))

# Sales/Invoices Routes
@app.route('/sales')
@login_required
def sales():
    invoices = Invoice.query.order_by(desc(Invoice.created_at)).all()
    return render_template('sales.html', 
                          title='Sales Management',
                          invoices=invoices)

@app.route('/invoices')
@login_required
def invoices():
    form = InvoiceForm()  # Add form instance for CSRF token
    all_invoices = Invoice.query.order_by(desc(Invoice.created_at)).all()
    return render_template('invoices.html', 
                          title='Invoice Management',
                          invoices=all_invoices,
                          form=form)

@app.route('/invoice/new', methods=['GET', 'POST'])
@login_required
def new_invoice():
    form = InvoiceForm()
    
    # Get customers for dropdown
    form.customer_id.choices = [(c.id, c.name) for c in Customer.query.all()]
    
    # Today's date for default values
    if request.method == 'GET':
        form.issue_date.data = datetime.now()
        form.due_date.data = datetime.now() + timedelta(days=30)
    
    return render_template('create_invoice.html', 
                          title='Create Invoice',
                          form=form,
                          products=Product.query.all(),
                          services=JewelryService.query.all())

@app.route('/api/product/<int:product_id>', methods=['GET'])
@login_required
def get_product_details(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'price': float(product.price),
        'available_quantity': product.quantity
    })
    
@app.route('/api/service/<int:service_id>', methods=['GET'])
@login_required
def get_service_details(service_id):
    service = JewelryService.query.get_or_404(service_id)
    return jsonify({
        'id': service.id,
        'name': service.name,
        'price': float(service.price),
        'service_type': service.service_type,
        'duration': service.duration,
        'requires_deposit': service.requires_deposit
    })
    
@app.route('/api/customer/create', methods=['POST'])
@login_required
def create_customer_api():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
    # Validate required fields
    if not data.get('name'):
        return jsonify({'status': 'error', 'message': 'Customer name is required'}), 400
        
    try:
        # Create new customer
        customer = Customer(
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
            preferences=data.get('preferences')
        )
        
        db.session.add(customer)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Customer created successfully',
            'customer': {
                'id': customer.id,
                'name': customer.name
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/invoice/save', methods=['POST'])
@login_required
def save_invoice():
    data = request.get_json()
    
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400
    
    try:
        # Create invoice
        invoice = Invoice(
            invoice_number=generate_invoice_number(),
            customer_id=data['customer_id'],
            issue_date=datetime.strptime(data['issue_date'], '%Y-%m-%d'),
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d') if data['due_date'] else None,
            total_amount=Decimal(data['total_amount']),
            tax_amount=Decimal(data['tax_amount']),
            discount=Decimal(data['discount']),
            final_amount=Decimal(data['final_amount']),
            
            # Jewelry store-specific invoice information
            is_custom_order=data.get('is_custom_order', False),
            is_repair=data.get('is_repair', False),
            estimated_ready_date=datetime.strptime(data['estimated_ready_date'], '%Y-%m-%d') if data.get('estimated_ready_date') else None,
            deposit_amount=Decimal(data.get('deposit_amount', 0)),
            warranty_period=data.get('warranty_period'),
            appraisal_value=Decimal(data.get('appraisal_value', 0)) if data.get('appraisal_value') else None,
            payment_method=data.get('payment_method'),
            
            status='pending',
            notes=data['notes'],
            created_by=current_user.id
        )
        
        db.session.add(invoice)
        db.session.flush()
        
        # Add invoice items
        for item in data['items']:
            is_service = item.get('is_service', False)
            service_id = item.get('service_id')
            
            invoice_item = InvoiceItem(
                invoice_id=invoice.id,
                product_id=item['product_id'],
                quantity=item['quantity'],
                unit_price=Decimal(item['unit_price']),
                total_price=Decimal(item['total_price']),
                is_service=is_service,
                service_id=service_id
            )
            db.session.add(invoice_item)
            
            # Only update product quantity if it's a product (not a service)
            if not is_service:
                product = Product.query.get(item['product_id'])
                if product:
                    product.quantity -= item['quantity']
        
        db.session.commit()
        
        # Return a success response with 200 status code
        return jsonify({
            'status': 'success', 
            'message': 'Invoice created successfully',
            'invoice_id': invoice.id,
            'success': True
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating invoice: {str(e)}")
        return jsonify({
            'status': 'error', 
            'message': str(e),
            'success': False
        }), 500

@app.route('/invoice/<int:invoice_id>')
@login_required
def view_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    form = InvoiceForm()  # Add form instance for CSRF token
    return render_template('view_invoice.html', 
                          title=f'Invoice #{invoice.invoice_number}',
                          invoice=invoice,
                          form=form)

@app.route('/invoice/<int:invoice_id>/status/<status>', methods=['POST'])
@login_required
def update_invoice_status(invoice_id, status):
    if status not in ['pending', 'paid', 'cancelled']:
        abort(400)
    
    invoice = Invoice.query.get_or_404(invoice_id)
    invoice.status = status
    db.session.commit()
    
    flash(f'Invoice status updated to {status}!', 'success')
    return redirect(url_for('view_invoice', invoice_id=invoice_id))

@app.route('/invoice/<int:invoice_id>/pdf')
@login_required
def generate_pdf(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    
    pdf_data = generate_invoice_pdf(invoice)
    
    response = make_response(pdf_data)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=invoice_{invoice.invoice_number}.pdf'
    
    return response

# Jewelry Services Routes
@app.route('/services')
@login_required
def services():
    all_services = JewelryService.query.all()
    return render_template('services.html', 
                          title='Jewelry Services',
                          services=all_services)

@app.route('/service/new', methods=['GET', 'POST'])
@login_required
def new_service():
    form = JewelryServiceForm()
    
    if form.validate_on_submit():
        service = JewelryService(
            name=form.name.data,
            description=form.description.data,
            service_type=form.service_type.data,
            price=form.price.data,
            duration=form.duration.data,
            materials_needed=form.materials_needed.data,
            difficulty_level=form.difficulty_level.data,
            requires_deposit=form.requires_deposit.data
        )
        db.session.add(service)
        db.session.commit()
        flash('Service has been created!', 'success')
        return redirect(url_for('services'))
    
    return render_template('services.html', 
                          title='New Service',
                          form=form, 
                          service_form=True)

@app.route('/service/<int:service_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_service(service_id):
    service = JewelryService.query.get_or_404(service_id)
    form = JewelryServiceForm()
    
    if form.validate_on_submit():
        service.name = form.name.data
        service.description = form.description.data
        service.service_type = form.service_type.data
        service.price = form.price.data
        service.duration = form.duration.data
        service.materials_needed = form.materials_needed.data
        service.difficulty_level = form.difficulty_level.data
        service.requires_deposit = form.requires_deposit.data
        service.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Service has been updated!', 'success')
        return redirect(url_for('services'))
    
    if request.method == 'GET':
        form.name.data = service.name
        form.description.data = service.description
        form.service_type.data = service.service_type
        form.price.data = service.price
        form.duration.data = service.duration
        form.materials_needed.data = service.materials_needed
        form.difficulty_level.data = service.difficulty_level
        form.requires_deposit.data = service.requires_deposit
    
    return render_template('services.html', 
                          title='Edit Service',
                          form=form, 
                          service_form=True)

@app.route('/service/<int:service_id>/delete', methods=['POST'])
@login_required
def delete_service(service_id):
    service = JewelryService.query.get_or_404(service_id)
    
    # Check if service is used in invoices
    if service.invoice_items:
        flash('Cannot delete service that has been used in invoices!', 'danger')
        return redirect(url_for('services'))
    
    db.session.delete(service)
    db.session.commit()
    flash('Service has been deleted!', 'success')
    return redirect(url_for('services'))

# Reports Routes
@app.route('/reports', methods=['GET', 'POST'])
@login_required
def reports():
    form = ReportForm()
    report_data = None
    
    if form.validate_on_submit():
        report_type = form.report_type.data
        start_date = form.start_date.data
        end_date = form.end_date.data or datetime.now()
        
        if report_type == 'sales':
            # Generate sales report
            query = db.session.query(
                func.date(Invoice.issue_date).label('date'),
                func.sum(Invoice.final_amount).label('total_sales'),
                func.count(Invoice.id).label('invoice_count')
            )
            
            if start_date:
                query = query.filter(Invoice.issue_date >= start_date)
            
            results = query.filter(
                Invoice.issue_date <= end_date,
                Invoice.status == 'paid'
            ).group_by(func.date(Invoice.issue_date)).order_by(func.date(Invoice.issue_date)).all()

            # Format data for JSON serialization
            formatted_data = [[row[0].strftime('%Y-%m-%d'), float(row[1]), row[2]] for row in results]
            
            report_data = {
                'type': 'sales',
                'title': 'Sales Report',
                'period': f"{start_date.strftime('%Y-%m-%d') if start_date else 'All'} to {end_date.strftime('%Y-%m-%d')}",
                'data': query.all(),
                'total': db.session.query(func.sum(Invoice.final_amount))
                    .filter(Invoice.status == 'paid')
                    .filter(Invoice.issue_date <= end_date)
                    .filter(Invoice.issue_date >= start_date if start_date else True).scalar() or 0
            }
            
        elif report_type == 'inventory':
            # Generate inventory report
            query = db.session.query(
                Product.name,
                Product.barcode,
                Category.name.label('category'),
                Product.quantity,
                Product.price,
                (Product.price * Product.quantity).label('total_value')
            ).join(Category)
            
            report_data = {
                'type': 'inventory',
                'title': 'Inventory Report',
                'period': datetime.now().strftime('%Y-%m-%d'),
                'data': query.all(),
                'total_items': db.session.query(func.sum(Product.quantity)).scalar() or 0,
                'total_value': db.session.query(func.sum(Product.price * Product.quantity)).scalar() or 0
            }
            
        elif report_type == 'customers':
            # Generate customer report
            query = db.session.query(
                Customer.name,
                Customer.email,
                Customer.phone,
                func.count(Invoice.id).label('invoice_count'),
                func.sum(Invoice.final_amount).label('total_spent')
            ).outerjoin(Invoice).filter(
                Invoice.status == 'paid' if start_date else True
            ).group_by(Customer.id)
            
            if start_date:
                query = query.filter(Invoice.issue_date >= start_date)
            
            if end_date:
                query = query.filter(Invoice.issue_date <= end_date)
                
            report_data = {
                'type': 'customers',
                'title': 'Customer Report',
                'period': f"{start_date.strftime('%Y-%m-%d') if start_date else 'All'} to {end_date.strftime('%Y-%m-%d')}",
                'data': query.all()
            }
    
    return render_template('reports.html', 
                         title='Reports',
                         form=form,
                         report_data=report_data)
