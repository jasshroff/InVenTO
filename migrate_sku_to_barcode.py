import os
import sys
import pymysql
from app import app, db
from models import Product

def migrate_sku_to_barcode():
    """
    This script migrates the database from using 'sku' to using 'barcode'
    and updates all existing products with auto-generated 5-digit barcodes.
    """
    try:
        # MySQL connection parameters from app config
        with app.app_context():
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
            
            # Parse MySQL connection parameters
            if not db_uri.startswith("mysql+pymysql://"):
                print("This script only supports MySQL databases.")
                return
                
            # Extract connection parameters from URI
            # mysql+pymysql://root:password@localhost/database
            credentials = db_uri.replace("mysql+pymysql://", "")
            user_pass, host_db = credentials.split("@")
            
            if ":" in user_pass:
                user, password = user_pass.split(":")
            else:
                user = user_pass
                password = ""
                
            if "/" in host_db:
                host, database = host_db.split("/")
            else:
                host = host_db
                database = ""
            
            print(f"Connecting to MySQL database: {database} at {host}")
            
            # Connect to MySQL database
            conn = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            cursor = conn.cursor()
            
            # Check if sku column exists
            cursor.execute("SHOW COLUMNS FROM product LIKE 'sku'")
            has_sku = cursor.fetchone() is not None
            
            cursor.execute("SHOW COLUMNS FROM product LIKE 'barcode'")
            has_barcode = cursor.fetchone() is not None
            
            if not has_sku:
                print("Column 'sku' not found in the 'product' table.")
                return
            
            if has_barcode:
                print("Column 'barcode' already exists in the 'product' table.")
                return
            
            # Rename SKU column to barcode and change type
            print("Renaming 'sku' column to 'barcode' and changing type to VARCHAR(5)...")
            cursor.execute("ALTER TABLE product CHANGE COLUMN sku barcode VARCHAR(5)")
            
            # Now, update all existing products with 5-digit barcodes
            print("Updating existing products with 5-digit barcodes...")
            
            # Get all products
            cursor.execute("SELECT id, barcode FROM product")
            products = cursor.fetchall()
            
            # Start with barcode 10000
            next_barcode = 10000
            
            for product_id, current_barcode in products:
                # Generate a new 5-digit barcode
                barcode = str(next_barcode).zfill(5)
                next_barcode += 1
                
                # Update the product with the new barcode
                cursor.execute(
                    "UPDATE product SET barcode = %s WHERE id = %s", 
                    (barcode, product_id)
                )
                print(f"Updated product {product_id}: Old barcode: {current_barcode}, New barcode: {barcode}")
            
            conn.commit()
            print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    migrate_sku_to_barcode() 