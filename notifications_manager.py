# notifications_manager.py
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

class NotificationsManager:
    """Manages notification states and dismissals for job applications."""
    
    def __init__(self, notifications_file: str = "notifications_state.json"):
        """Initialize the notifications manager.
        
        Args:
            notifications_file (str): Path to the notifications state file
        """
        self.notifications_file = Path(notifications_file)
        self.setup_logging()
        self.load_state()
        self.ensure_backup()
        
    def setup_logging(self) -> None:
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('notifications.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def ensure_backup(self) -> None:
        """Ensure a backup of the notifications state exists."""
        try:
            if self.notifications_file.exists():
                backup_file = self.notifications_file.with_suffix('.json.bak')
                if not backup_file.exists():
                    backup_file.write_text(self.notifications_file.read_text())
        except Exception as e:
            self.logger.error(f"Error creating backup: {str(e)}")
                
    def load_state(self) -> None:
        """Load notification states from file with error handling."""
        try:
            if self.notifications_file.exists():
                with open(self.notifications_file, 'r', encoding='utf-8') as f:
                    self.state = json.load(f)
                    
                # Validate state structure
                if not isinstance(self.state, dict):
                    raise ValueError("Invalid state structure")
                    
                if "last_reset" not in self.state or "dismissals" not in self.state:
                    raise ValueError("Missing required state fields")
                    
            else:
                self.state = {
                    "last_reset": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "dismissals": {}
                }
                self.save_state()
                
        except Exception as e:
            self.logger.error(f"Error loading notification state: {str(e)}")
            # Try to load from backup
            backup_file = self.notifications_file.with_suffix('.json.bak')
            if backup_file.exists():
                try:
                    with open(backup_file, 'r', encoding='utf-8') as f:
                        self.state = json.load(f)
                except:
                    self._create_default_state()
            else:
                self._create_default_state()
                
    def _create_default_state(self) -> None:
        """Create default notification state."""
        self.state = {
            "last_reset": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "dismissals": {}
        }
        self.save_state()
                
    def save_state(self) -> bool:
        """Save notification states to file with error handling."""
        try:
            # Create backup before saving
            if self.notifications_file.exists():
                backup_file = self.notifications_file.with_suffix('.json.bak')
                backup_file.write_text(self.notifications_file.read_text())
                
            # Save new state
            with open(self.notifications_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving notification state: {str(e)}")
            return False
            
    def check_reset_needed(self) -> bool:
        """Check if dismissals need to be reset (24 hour period)."""
        last_reset = self.state.get("last_reset", "")
        if not last_reset:
            return True
            
        try:
            last_reset_date = datetime.strptime(last_reset, "%Y-%m-%d %H:%M:%S")
            return datetime.now() - last_reset_date > timedelta(hours=24)
        except Exception as e:
            self.logger.error(f"Error checking reset: {str(e)}")
            return True
            
    def reset_if_needed(self) -> None:
        """Reset dismissals if 24 hours have passed."""
        try:
            if self.check_reset_needed():
                self.state["dismissals"] = {}
                self.state["last_reset"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.save_state()
        except Exception as e:
            self.logger.error(f"Error resetting state: {str(e)}")
            
    def is_dismissed(self, app_id: str) -> bool:
        """Check if an application notification is dismissed."""
        return app_id in self.state["dismissals"]
        
    def dismiss_notification(self, app_id: str) -> None:
        """Dismiss a notification for an application."""
        try:
            self.state["dismissals"][app_id] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.save_state()
        except Exception as e:
            self.logger.error(f"Error dismissing notification: {str(e)}")
            
    def get_dismiss_age(self, app_id: str) -> Optional[timedelta]:
        """Get the age of a dismissal."""
        if app_id not in self.state["dismissals"]:
            return None
            
        try:
            dismiss_time = datetime.strptime(
                self.state["dismissals"][app_id],
                "%Y-%m-%d %H:%M:%S"
            )
            return datetime.now() - dismiss_time
        except Exception as e:
            self.logger.error(f"Error getting dismissal age: {str(e)}")
            return None
            
    def get_pending_notifications(self, applications: List[Dict]) -> List[Dict]:
        """Get list of applications needing update checks with prioritization."""
        try:
            self.reset_if_needed()
            self.cleanup_old_dismissals()
            
            # Filter pending applications
            pending = [app for app in applications 
                      if app['status'] in ['applied', 'not_applied']
                      and not self.is_dismissed(app['id'])]
                      
            # Sort by application age (older first)
            pending.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'))
            
            return pending
        except Exception as e:
            self.logger.error(f"Error getting pending notifications: {str(e)}")
            return []

    def cleanup_old_dismissals(self) -> None:
        """Remove dismissals older than 48 hours."""
        try:
            now = datetime.now()
            to_remove = []
            
            for app_id, dismiss_time in self.state["dismissals"].items():
                dismissed_at = datetime.strptime(dismiss_time, "%Y-%m-%d %H:%M:%S")
                if now - dismissed_at > timedelta(hours=48):
                    to_remove.append(app_id)
                    
            if to_remove:
                for app_id in to_remove:
                    del self.state["dismissals"][app_id]
                self.save_state()
        except Exception as e:
            self.logger.error(f"Error cleaning up dismissals: {str(e)}")