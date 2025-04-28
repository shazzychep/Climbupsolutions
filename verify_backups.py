import subprocess
import os
import datetime
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def verify_postgres_backup(backup_file):
    """Verify PostgreSQL backup integrity"""
    try:
        # Check if file exists
        if not os.path.exists(backup_file):
            logger.error(f"Backup file not found: {backup_file}")
            return False
        
        # Verify gzip integrity
        result = subprocess.run(['gzip', '-t', backup_file], capture_output=True)
        if result.returncode != 0:
            logger.error(f"Gzip integrity check failed: {result.stderr.decode()}")
            return False
        
        logger.info(f"PostgreSQL backup verified: {backup_file}")
        return True
    except Exception as e:
        logger.error(f"Error verifying PostgreSQL backup: {str(e)}")
        return False

def verify_mongodb_backup(backup_file):
    """Verify MongoDB backup integrity"""
    try:
        # Check if file exists
        if not os.path.exists(backup_file):
            logger.error(f"Backup file not found: {backup_file}")
            return False
        
        # Verify archive integrity
        result = subprocess.run(['mongorestore', '--dryRun', '--archive=' + backup_file], 
                              capture_output=True)
        if result.returncode != 0:
            logger.error(f"MongoDB archive check failed: {result.stderr.decode()}")
            return False
        
        logger.info(f"MongoDB backup verified: {backup_file}")
        return True
    except Exception as e:
        logger.error(f"Error verifying MongoDB backup: {str(e)}")
        return False

def check_backup_schedule():
    """Verify backup schedule is running as expected"""
    try:
        # Get current date
        today = datetime.datetime.now().strftime('%Y%m%d')
        
        # Check PostgreSQL backup
        postgres_backup = f"/backup/postgres-{today}.sql.gz"
        if not verify_postgres_backup(postgres_backup):
            logger.error("PostgreSQL backup verification failed")
            return False
        
        # Check MongoDB backup
        mongodb_backup = f"/backup/mongodb-{today}.archive"
        if not verify_mongodb_backup(mongodb_backup):
            logger.error("MongoDB backup verification failed")
            return False
        
        logger.info("All backups verified successfully")
        return True
    except Exception as e:
        logger.error(f"Error checking backup schedule: {str(e)}")
        return False

if __name__ == "__main__":
    # Create backup directory if it doesn't exist
    Path("/backup").mkdir(parents=True, exist_ok=True)
    
    # Run verification
    if check_backup_schedule():
        logger.info("Backup verification completed successfully")
    else:
        logger.error("Backup verification failed")
        exit(1) 