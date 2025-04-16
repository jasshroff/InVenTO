from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    products = db.relationship('Product', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    products = db.relationship('Product', backref='supplier', lazy=True)
    
    def __repr__(self):
        return f'<Supplier {self.name}>'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    barcode = db.Column(db.String(5), unique=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    cost_price = db.Column(db.Numeric(10, 2))
    quantity = db.Column(db.Integer, default=0)
    
    # Jewelry-specific attributes
    material = db.Column(db.String(50))
    metal_type = db.Column(db.String(50))
    purity = db.Column(db.String(20))  # For gold/silver purity (e.g., "18K", "925")
    stone_type = db.Column(db.String(50))
    stone_count = db.Column(db.Integer, default=0)
    stone_carat = db.Column(db.Numeric(10, 2), default=0)
    weight = db.Column(db.Numeric(10, 3))  # Weight in grams with 3 decimal places
    size = db.Column(db.String(20))  # For rings, bracelets, etc.
    
    # Foreign keys and timestamps
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    invoice_items = db.relationship('InvoiceItem', backref='product', lazy=True)
    
    def __repr__(self):
        return f'<Product {self.name}>'

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    
    # Jewelry store customer-specific information
    birthdate = db.Column(db.Date)
    anniversary = db.Column(db.Date)
    preferences = db.Column(db.Text)  # Customer's style preferences
    ring_size = db.Column(db.String(10))
    bracelet_size = db.Column(db.String(10))
    necklace_length = db.Column(db.String(10))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    invoices = db.relationship('Invoice', backref='customer', lazy=True)
    
    def __repr__(self):
        return f'<Customer {self.name}>'

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    
    # Financial information
    total_amount = db.Column(db.Numeric(10, 2), default=0)
    tax_amount = db.Column(db.Numeric(10, 2), default=0)
    discount = db.Column(db.Numeric(10, 2), default=0)
    final_amount = db.Column(db.Numeric(10, 2), default=0)
    
    # Jewelry store-specific invoice information
    is_custom_order = db.Column(db.Boolean, default=False)
    is_repair = db.Column(db.Boolean, default=False)
    estimated_ready_date = db.Column(db.DateTime)
    deposit_amount = db.Column(db.Numeric(10, 2), default=0)
    warranty_period = db.Column(db.Integer)  # Warranty period in months
    appraisal_value = db.Column(db.Numeric(10, 2))  # For insurance purposes
    
    # Common fields
    status = db.Column(db.String(20), default='pending')  # pending, paid, cancelled, layaway
    payment_method = db.Column(db.String(50))  # cash, credit, debit, etc.
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'

class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Jewelry-specific fields
    is_service = db.Column(db.Boolean, default=False)  # Is this a product or a service
    service_id = db.Column(db.Integer, db.ForeignKey('jewelry_service.id'), nullable=True)
    
    def __repr__(self):
        return f'<InvoiceItem {self.id}>'

class JewelryService(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    service_type = db.Column(db.String(50), nullable=False)  # repair, cleaning, engraving, custom, etc.
    price = db.Column(db.Numeric(10, 2), nullable=False)
    duration = db.Column(db.Integer)  # Estimated duration in days
    
    # Service requirements and options
    materials_needed = db.Column(db.Text)
    difficulty_level = db.Column(db.String(20))  # easy, medium, complex
    requires_deposit = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    invoice_items = db.relationship('InvoiceItem', backref='service', lazy=True)
    
    def __repr__(self):
        return f'<JewelryService {self.name}>'
