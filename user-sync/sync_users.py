#!/usr/bin/env python3
"""
OpenWebUI to LiteLLM User Synchronization Service
Automatically creates internal users in LiteLLM when new users are created in OpenWebUI
Reads directly from OpenWebUI's SQLite database
"""

import os
import sys
import time
import logging
import requests
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

# Configuration from environment variables
OPENWEBUI_DB_PATH = os.getenv("OPENWEBUI_DB_PATH", "/openwebui-data/webui.db")
LITELLM_URL = os.getenv("LITELLM_URL", "http://litellm:4000")
LITELLM_MASTER_KEY = os.getenv("LITELLM_MASTER_KEY")
SYNC_INTERVAL = int(os.getenv("SYNC_INTERVAL", "60"))  # seconds
DEFAULT_USER_BUDGET = float(os.getenv("DEFAULT_USER_BUDGET", "100"))
DEFAULT_USER_ROLE = os.getenv("DEFAULT_USER_ROLE", "internal_user")

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class UserSyncService:
    def __init__(self):
        self.validate_config()
        
    def validate_config(self):
        """Validate required environment variables"""
        if not LITELLM_MASTER_KEY:
            logger.error("LITELLM_MASTER_KEY is not set!")
            sys.exit(1)
        
        if not os.path.exists(OPENWEBUI_DB_PATH):
            logger.error(f"OpenWebUI database not found at {OPENWEBUI_DB_PATH}")
            logger.error("Make sure the OpenWebUI data volume is mounted correctly")
            sys.exit(1)
        
        logger.info("Configuration validated successfully")
        logger.info(f"OpenWebUI DB: {OPENWEBUI_DB_PATH}")
        logger.info(f"LiteLLM URL: {LITELLM_URL}")
        logger.info(f"Sync interval: {SYNC_INTERVAL}s")
    
    def get_openwebui_users(self) -> List[Dict]:
        """Fetch all users from OpenWebUI SQLite database"""
        try:
            conn = sqlite3.connect(OPENWEBUI_DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Query the user table
            cursor.execute("SELECT id, email, name, role FROM user")
            rows = cursor.fetchall()
            
            users = []
            for row in rows:
                users.append({
                    "id": row["id"],
                    "email": row["email"] if row["email"] else f"{row['id']}@local",
                    "name": row["name"] if row["name"] else "Unknown",
                    "role": row["role"] if row["role"] else "user"
                })
            
            conn.close()
            logger.debug(f"Found {len(users)} users in OpenWebUI database")
            return users
            
        except sqlite3.Error as e:
            logger.error(f"Failed to read OpenWebUI database: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error reading OpenWebUI users: {e}")
            return []
    
    def get_litellm_users(self) -> Dict[str, Dict]:
        """Fetch all users from LiteLLM and return as a dict keyed by user_id"""
        try:
            response = requests.get(
                f"{LITELLM_URL}/user/info",
                headers={"Authorization": f"Bearer {LITELLM_MASTER_KEY}"},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            users = {}
            if isinstance(data, dict) and "users" in data:
                for user in data["users"]:
                    users[user.get("user_id")] = user
            
            logger.debug(f"Found {len(users)} users in LiteLLM")
            return users
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch LiteLLM users: {e}")
            return {}
    
    def create_litellm_user(self, user_data: Dict) -> Optional[Dict]:
        """Create a new internal user in LiteLLM"""
        try:
            payload = {
                "user_id": user_data["id"],
                "user_email": user_data.get("email", f"{user_data['id']}@local"),
                "user_role": DEFAULT_USER_ROLE,
                "max_budget": DEFAULT_USER_BUDGET,
                "models": ["*"],  # Access to all models
                "metadata": {
                    "synced_from": "openwebui",
                    "synced_at": datetime.utcnow().isoformat(),
                    "openwebui_name": user_data.get("name", "Unknown")
                }
            }
            
            response = requests.post(
                f"{LITELLM_URL}/user/new",
                headers={
                    "Authorization": f"Bearer {LITELLM_MASTER_KEY}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"✅ Created LiteLLM user: {user_data.get('email')} (ID: {user_data['id']})")
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to create LiteLLM user {user_data.get('email')}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            return None
    
    def sync_users(self):
        """Main sync logic: compare users and create missing ones in LiteLLM"""
        logger.info("🔄 Starting user synchronization...")
        
        openwebui_users = self.get_openwebui_users()
        litellm_users = self.get_litellm_users()
        
        if not openwebui_users:
            logger.warning("No users found in OpenWebUI or connection failed")
            return
        
        created_count = 0
        for user in openwebui_users:
            user_id = user.get("id")
            if not user_id:
                continue
            
            if user_id not in litellm_users:
                logger.info(f"🆕 New user detected: {user.get('email', user_id)}")
                if self.create_litellm_user(user):
                    created_count += 1
        
        if created_count > 0:
            logger.info(f"✨ Sync complete: {created_count} new user(s) created in LiteLLM")
        else:
            logger.info("✓ Sync complete: All users already synchronized")
    
    def run(self):
        """Main loop: run sync periodically"""
        logger.info("🚀 User Sync Service started")
        logger.info(f"Default user budget: ${DEFAULT_USER_BUDGET}")
        logger.info(f"Default user role: {DEFAULT_USER_ROLE}")
        
        # Initial sync
        self.sync_users()
        
        # Periodic sync
        while True:
            try:
                time.sleep(SYNC_INTERVAL)
                self.sync_users()
            except KeyboardInterrupt:
                logger.info("Shutting down gracefully...")
                break
            except Exception as e:
                logger.error(f"Unexpected error in sync loop: {e}")
                time.sleep(SYNC_INTERVAL)


if __name__ == "__main__":
    service = UserSyncService()
    service.run()
