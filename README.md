
# Jewelry Store Management System\

username-jshroff
email:- jshroff200@gmail.com
password:- 

username-jasshroff1
email:- jasshroff@gmail.com
password:- Apple123

username :- neil 
email :- neilrajeshshirke2019@gmail.com
password:- Neil123



A Flask-based web application for managing a jewellery store's inventory, sales, and customer relationships.

## Prerequisites

- Python 3.11 or higher
- MySQL
- Required Python packages (installed automatically via pyproject.toml)
- BOOTSTRAP
- HTML
- CSS
- JAVASCRIPT

## Setup Steps

1. **Database Setup**
   - Make sure MySQL is running
   - Set the `DATABASE_URL` environment variable in your App.py
   - Set the `SESSION_SECRET` environment variable in your App.py

2. **Database Migration**
   Run the database migration script to set up all required tables:
   ```bash
   python migrate_db.py
   ```

3. **Starting the Application**
   The application can be started using:
   ```bash
   python main.py
   ```
   Or using gunicorn (recommended for production):
   ```bash
   gunicorn --bind 0.0.0.0:5000 main:app
   ```

4. **First Time Setup**
   - Register a new user account at `/register`
   - Log in with your credentials
   - Start adding products, customers, and services

## Features

- Product Inventory Management
- Customer Management
- Invoice Generation
- Sales Reporting
- Service Management
- Customer Preferences Tracking

## File Structure

- `app.py` - Main application configuration
- `main.py` - Application entry point
- `routes.py` - All route handlers
- `models.py` - Database models
- `forms.py` - Form definitions
- `utils.py` - Utility functions
- `migrate_db.py` - Database migration script
- `static/` - Static files (CSS, JS)
- `templates/` - HTML templates

## Important Notes

- The application runs on port 5000 by default
- Make sure to properly set up environment variables before running
- Backup your database regularly
