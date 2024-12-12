import sqlite3
from datetime import datetime
from typing import Dict, Optional
from .logger import LoggerManager

class DatabaseManager:
    def __init__(
            self, 
            db_path : str = "usage_stats.db" 
    ):
        self.db_path = db_path
        self.logger = LoggerManager.get_logger(__name__)
        self.logger.info("DatabaseManager initialized")
        self._init_db()

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS window_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        process_name TEXT NOT NULL,
                        window_title TEXT NOT NULL,
                        start_time DATETIME NOT NULL,
                        end_time DATETIME NOT NULL,
                        duration INTEGER NOT NULL
                    )
                """)
        except sqlite3.Error as e:
            self.logger.error(f"Error initializing database: {e}")
            raise

    def record_window_usage(
            self, 
    ):

