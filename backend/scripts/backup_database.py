#!/usr/bin/env python3
import os
import sys
import logging
import shutil
from datetime import datetime
from pathlib import Path
import subprocess
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseBackup:
    def __init__(self, backup_dir: str = "backups", max_backups: int = 7):
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def _get_database_url(self) -> Optional[str]:
        """Get database URL from environment or config"""
        return os.getenv("DATABASE_URL")

    def _create_backup_filename(self) -> str:
        """Create backup filename with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"qa_database_backup_{timestamp}.sql"

    def _cleanup_old_backups(self):
        """Remove old backups keeping only max_backups"""
        backups = sorted(self.backup_dir.glob("*.sql"))
        while len(backups) >= self.max_backups:
            oldest_backup = backups.pop(0)
            logger.info(f"Removing old backup: {oldest_backup}")
            oldest_backup.unlink()

    def backup_postgres(self):
        """Backup PostgreSQL database"""
        try:
            db_url = self._get_database_url()
            if not db_url or not db_url.startswith("postgresql"):
                raise ValueError("PostgreSQL database URL not found")

            # Parse database URL
            db_parts = db_url.replace("postgresql://", "").split("@")
            if len(db_parts) != 2:
                raise ValueError("Invalid database URL format")

            auth, host_db = db_parts
            user, password = auth.split(":")
            host, db = host_db.split("/")

            # Set environment variables for pg_dump
            env = os.environ.copy()
            env["PGPASSWORD"] = password

            # Create backup filename
            backup_file = self.backup_dir / self._create_backup_filename()

            # Execute pg_dump
            cmd = [
                "pg_dump",
                "-h", host,
                "-U", user,
                "-d", db,
                "-F", "c",  # Custom format
                "-f", str(backup_file)
            ]

            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"pg_dump failed: {result.stderr}")

            logger.info(f"Database backup created: {backup_file}")
            self._cleanup_old_backups()

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            raise

    def backup_sqlite(self):
        """Backup SQLite database"""
        try:
            db_url = self._get_database_url()
            if not db_url or not db_url.startswith("sqlite"):
                raise ValueError("SQLite database URL not found")

            # Get database path
            db_path = db_url.replace("sqlite:///", "")
            if not os.path.exists(db_path):
                raise FileNotFoundError(f"Database file not found: {db_path}")

            # Create backup filename
            backup_file = self.backup_dir / self._create_backup_filename()

            # Copy database file
            shutil.copy2(db_path, backup_file)
            logger.info(f"Database backup created: {backup_file}")
            self._cleanup_old_backups()

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            raise

    def backup(self):
        """Create database backup based on database type"""
        try:
            db_url = self._get_database_url()
            if not db_url:
                raise ValueError("Database URL not found")

            if db_url.startswith("postgresql"):
                self.backup_postgres()
            elif db_url.startswith("sqlite"):
                self.backup_sqlite()
            else:
                raise ValueError(f"Unsupported database type: {db_url.split('://')[0]}")

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    backup = DatabaseBackup()
    backup.backup()