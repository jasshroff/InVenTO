from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, DecimalField, IntegerField, SelectField, DateField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional, NumberRange
from models import User, Category, Supplier, Product, Customer

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered. Please use a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    submit = SubmitField('Submit')
    
    def validate_name(self, name):
        if self.original_name and self.original_name == name.data:
            return
        category = Category.query.filter_by(name=name.data).first()
        if category:
            raise ValidationError('Category name already exists. Please choose a different one.')

class SupplierForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    contact_person = StringField('Contact Person', validators=[Length(max=100)])
    email = StringField('Email', validators=[Email(), Optional()])
    phone = StringField('Phone', validators=[Length(max=20)])
    address = TextAreaField('Address')
    submit = SubmitField('Submit')

class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    barcode = StringField('Barcode', validators=[Length(max=5)], render_kw={'readonly': True})
    price = DecimalField('Sales Price', places=2, validators=[DataRequired(), NumberRange(min=0)])
    cost_price = DecimalField('Cost Price', places=2, validators=[NumberRange(min=0), Optional()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    
    # Jewelry-specific attributes
    material = StringField('Material', validators=[Length(max=50), Optional()])
    metal_type = StringField('Metal Type', validators=[Length(max=50), Optional()])
    purity = StringField('Purity (e.g., 18K, 925)', validators=[Length(max=20), Optional()])
    stone_type = StringField('Stone Type', validators=[Length(max=50), Optional()])
    stone_count = IntegerField('Number of Stones', default=0, validators=[NumberRange(min=0), Optional()])
    stone_carat = DecimalField('Stone Carat Weight', places=2, validators=[NumberRange(min=0), Optional()])
    weight = DecimalField('Weight (grams)', places=3, validators=[NumberRange(min=0), Optional()])
    size = StringField('Size (for rings, bracelets, etc.)', validators=[Length(max=20), Optional()])
    
    # Foreign keys
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    supplier_id = SelectField('Supplier', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')
    
    def validate_barcode(self, barcode):
        if barcode.data and self.original_barcode and self.original_barcode == barcode.data:
            return
        if barcode.data:
            product = Product.query.filter_by(barcode=barcode.data).first()
            if product:
                raise ValidationError('Barcode already exists. Please choose a different one.')

class CustomerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[Email(), Optional()])
    phone = StringField('Phone', validators=[Length(max=20)])
    address = TextAreaField('Address')
    
    # Jewelry store customer-specific information
    birthdate = DateField('Birthdate', validators=[Optional()])
    anniversary = DateField('Anniversary', validators=[Optional()])
    preferences = TextAreaField('Style Preferences', validators=[Optional()])
    ring_size = StringField('Ring Size', validators=[Length(max=10), Optional()])
    bracelet_size = StringField('Bracelet Size', validators=[Length(max=10), Optional()])
    necklace_length = StringField('Preferred Necklace Length', validators=[Length(max=10), Optional()])
    
    submit = SubmitField('Submit')

class SimpleCustomerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[Email(), Optional()])
    phone = StringField('Phone', validators=[Length(max=20)])
    address = TextAreaField('Address')
    preferences = TextAreaField('Style Preferences/Description', validators=[Optional()])
    submit = SubmitField('Add Customer')

class InvoiceForm(FlaskForm):
    customer_id = SelectField('Customer', coerce=int, validators=[DataRequired()])
    issue_date = DateField('Issue Date', validators=[DataRequired()])
    due_date = DateField('Due Date', validators=[Optional()])
    
    # Jewelry store-specific fields
    is_custom_order = BooleanField('Custom Order')
    is_repair = BooleanField('Repair/Service')
    estimated_ready_date = DateField('Estimated Ready Date', validators=[Optional()])
    deposit_amount = DecimalField('Deposit Amount', places=2, validators=[NumberRange(min=0), Optional()])
    warranty_period = IntegerField('Warranty Period (months)', validators=[NumberRange(min=0), Optional()])
    appraisal_value = DecimalField('Appraisal Value', places=2, validators=[NumberRange(min=0), Optional()])
    payment_method = SelectField('Payment Method', choices=[
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('layaway', 'Layaway Plan')
    ], validators=[Optional()])
    
    # Common fields
    notes = TextAreaField('Notes')
    discount = DecimalField('Discount', places=2, validators=[NumberRange(min=0), Optional()])
    submit = SubmitField('Create Invoice')

class InvoiceItemForm(FlaskForm):
    product_id = SelectField('Product', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    unit_price = DecimalField('Unit Price', places=2, validators=[DataRequired(), NumberRange(min=0)])
    
    # Service-related fields
    is_service = BooleanField('Is Service')
    service_id = SelectField('Service Type', coerce=int, validators=[Optional()])
    
    submit = SubmitField('Add Item')

class JewelryServiceForm(FlaskForm):
    name = StringField('Service Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    service_type = SelectField('Service Type', choices=[
        ('repair', 'Repair'),
        ('custom', 'Custom Design'),
        ('cleaning', 'Cleaning'),
        ('engraving', 'Engraving'),
        ('appraisal', 'Appraisal'),
        ('sizing', 'Sizing'),
        ('stone_setting', 'Stone Setting'),
        ('polishing', 'Polishing'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    price = DecimalField('Service Price', places=2, validators=[DataRequired(), NumberRange(min=0)])
    duration = IntegerField('Estimated Duration (days)', validators=[NumberRange(min=1), Optional()])
    materials_needed = TextAreaField('Materials Needed', validators=[Optional()])
    difficulty_level = SelectField('Difficulty Level', choices=[
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('complex', 'Complex')
    ], validators=[Optional()])
    requires_deposit = BooleanField('Requires Deposit')
    submit = SubmitField('Submit')

class ReportForm(FlaskForm):
    report_type = SelectField('Report Type', choices=[
        ('sales', 'Sales Report'),
        ('inventory', 'Inventory Report'),
        ('customers', 'Customer Report'),
        ('services', 'Services Report')
    ], validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[Optional()])
    end_date = DateField('End Date', validators=[Optional()])
    submit = SubmitField('Generate Report')
