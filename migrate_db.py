import os
import logging
from app import app, db
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migrations():
    """Run database migrations manually"""
    try:
        with app.app_context():
            connection = db.engine.connect()
            transaction = connection.begin()

            try:
                # All table creation is handled by SQLAlchemy's create_all()
                db.create_all()
                logger.info("Database tables created successfully!")

                transaction.commit()
                logger.info("Database migration completed successfully!")

            except Exception as e:
                transaction.rollback()
                logger.error(f"Error during migration: {str(e)}")
                raise
            finally:
                connection.close()

    except Exception as e:
        logger.error(f"Database migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    run_migrations()
    print("Database migration completed.")