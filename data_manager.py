# data_manager.py
import json
import logging
from pathlib import Path
from typing import List, Dict

class DataManager:
    """Handles all data operations for the Job Tracker application."""
    
    def __init__(self, data_file: str):
        self.data_file = Path(data_file)
        self.setup_logging()
        
    def setup_logging(self) -> None:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('job_tracker.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def validate_application(self, app: Dict) -> bool:
        required_fields = ['company', 'position', 'status', 'date', 'id']
        return all(field in app and app[field] for field in required_fields)
        
    def load_data(self) -> List[Dict]:
        self.logger.info(f"Loading data from {self.data_file}")
        
        if not self.data_file.exists():
            self.logger.info("Data file not found. Creating new file.")
            self.save_data([])
            return []
            
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if not isinstance(data, list):
                self.logger.error("Invalid data structure: not a list")
                return []
                
            # Clean and validate data
            valid_data = []
            for app in data:
                if self.validate_application(app):
                    # Ensure ID is string and stripped
                    app['id'] = str(app['id']).strip()
                    valid_data.append(app)
                    
            if len(valid_data) != len(data):
                self.logger.warning(
                    f"Found {len(data) - len(valid_data)} invalid entries"
                )
            
            self.logger.info(f"Successfully loaded {len(valid_data)} applications")
            return valid_data
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {str(e)}")
            backup_file = self.data_file.with_suffix('.json.bak')
            self.data_file.rename(backup_file)
            self.logger.info(f"Backed up corrupted file to {backup_file}")
            return []
            
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            return []
            
    def save_data(self, applications: List[Dict]) -> bool:
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(applications, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Successfully saved {len(applications)} applications")
            return True
        except Exception as e:
            self.logger.error(f"Error saving data: {str(e)}")
            return False