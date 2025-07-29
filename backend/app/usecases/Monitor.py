"""
backend/app/usecases/Monitor.py
------------------------------------
Monitor Use Case - Responsible for monitoring data flow and triggering alarms
"""
import sys
import os
import logging
import threading
from pathlib import Path
from typing import List, Callable, Optional, Dict, Any
from datetime import datetime, timedelta

# Add backend directory to Python path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from backend.app.entities.record import Record
from backend.app.entities.rule import Rule
from backend.app.entities.AlarmEvent import AlarmEvent
from backend.app.services.RuleEngineService import RuleEngine
from backend.app.infra.datastore.DatParser import iter_new_records
from backend.app.infra.config.RuleLoader import RuleLoader
from backend.app.infra.fileprovider import FileProvider
from backend.app.interfaces.IMonitorService import IMonitorService
from backend.app.interfaces.IFileProvider import IFileProvider


class MonitorService(IMonitorService):
    """
    Monitor Service
    
    Coordinates data parsing, rule evaluation, and alarm processing
    Supports FileProvider's continuous monitoring functionality
    """
    
    def __init__(self):
        self.rule_engine = RuleEngine()
        self.rule_loader = RuleLoader()
        self.logger = logging.getLogger(__name__)
        self.alarm_handlers: List[Callable[[AlarmEvent], None]] = []
        
        # FileProvider related
        self.file_provider: Optional[IFileProvider] = None
        self.monitoring_thread: Optional[threading.Thread] = None
        self.stop_monitoring_event = threading.Event()
        self._is_monitoring = False
        
        # Monitoring status
        self.monitoring_stats = {
            'total_records_processed': 0,
            'total_alarms_generated': 0,
            'last_processed_time': None,
            'current_file_path': None
        }
    
    def initialize(self, config_path: str = "config/rules.yaml") -> None:
        """
        Initialize monitor service
        
        Parameters
        ----------
        config_path : str
            Path to rule configuration file
        """
        try:
            # Load rules
            rules = self.rule_loader.load_rules()
            self.rule_engine.load_rules(rules)
            self.logger.info(f"Monitor service initialized, loaded {len(rules)} rules")
        except Exception as e:
            self.logger.error(f"Failed to initialize monitor service: {e}")
            raise
    
    def set_file_provider(self, file_provider: IFileProvider) -> None:
        """
        Set file provider
        
        Parameters
        ----------
        file_provider : IFileProvider
            File provider instance
        """
        self.file_provider = file_provider
        # Set file update callback
        file_provider.set_callback(self._on_file_update)
        self.logger.info("File provider set")
    
    def start_continuous_monitoring(self, run_id: str) -> bool:
        """
        Start continuous monitoring
        
        Parameters
        ----------
        run_id : str
            Test session ID
            
        Returns
        -------
        bool
            True if monitoring started successfully
        """
        if self._is_monitoring:
            self.logger.warning("Monitoring already running")
            return False
        
        try:
            self.stop_monitoring_event.clear()
            self._is_monitoring = True
            
            # Start monitoring thread
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_worker,
                args=(run_id,),
                daemon=True
            )
            self.monitoring_thread.start()
            
            self.logger.info(f"Continuous monitoring started for run_id: {run_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start continuous monitoring: {e}")
            self._is_monitoring = False
            return False
    
    def stop_continuous_monitoring(self) -> bool:
        """
        Stop continuous monitoring
        
        Returns
        -------
        bool
            True if monitoring stopped successfully
        """
        if not self._is_monitoring:
            return True
        
        try:
            self.stop_monitoring_event.set()
            self._is_monitoring = False
            
            # Stop file provider
            if self.file_provider:
                self.file_provider.stop()
            
            # Wait for thread to finish
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=5)
            
            self.logger.info("Continuous monitoring stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop continuous monitoring: {e}")
            return False
    
    def add_alarm_handler(self, handler: Callable[[AlarmEvent], None]) -> None:
        """
        Add alarm handler
        
        Parameters
        ----------
        handler : Callable[[AlarmEvent], None]
            Alarm handler function
        """
        self.alarm_handlers.append(handler)
    
    def process_data_file(self, file_path: str, run_id: str) -> tuple[List[AlarmEvent], int]:
        """
        Process data file
        
        Parameters
        ----------
        file_path : str
            Path to data file
        run_id : str
            Run ID
            
        Returns
        -------
        tuple[List[AlarmEvent], int]
            List of alarms and record count
        """
        alarms = []
        records_count = 0
        
        try:
            for record in iter_new_records(file_path):
                record_alarms = self.process_record(record, run_id)
                alarms.extend(record_alarms)
                records_count += 1
                
                # Update stats
                self.monitoring_stats['total_records_processed'] += 1
                self.monitoring_stats['total_alarms_generated'] += len(record_alarms)
                self.monitoring_stats['last_processed_time'] = datetime.now()
                self.monitoring_stats['current_file_path'] = file_path
            
            self.logger.info(f"Processed {records_count} records, generated {len(alarms)} alarms")
            
        except Exception as e:
            self.logger.error(f"Failed to process data file: {e}")
            raise
        
        return alarms, records_count
    
    def process_record(self, record: Record, run_id: str) -> List[AlarmEvent]:
        """
        Process single record
        
        Parameters
        ----------
        record : Record
            Sensor record
        run_id : str
            Run ID
            
        Returns
        -------
        List[AlarmEvent]
            List of generated alarms
        """
        try:
            # Evaluate rules
            alarms = self.rule_engine.evaluate_record(record, run_id)
            
            # Handle alarms
            for alarm in alarms:
                self._handle_alarm(alarm)
            
            return alarms
            
        except Exception as e:
            self.logger.error(f"Failed to process record: {e}")
            return []
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """
        Get monitoring status
        
        Returns
        -------
        Dict[str, Any]
            Current monitoring status
        """
        status = {
            'is_monitoring': self._is_monitoring,
            'stats': self.monitoring_stats.copy()
        }
        
        if self.file_provider:
            status['file_provider'] = self.file_provider.get_status()
        
        return status
    
    @property
    def is_monitoring(self) -> bool:
        """
        Check if monitoring is active
        
        Returns
        -------
        bool
            True if monitoring is active
        """
        return self._is_monitoring
    
    def _on_file_update(self, file_path: Path):
        """
        Handle file update callback
        
        Parameters
        ----------
        file_path : Path
            Updated file path
        """
        try:
            self.logger.info(f"File updated: {file_path}")
            
            # Process new records
            for record in iter_new_records(str(file_path)):
                record_alarms = self.process_record(record, "continuous")
                
                # Update stats
                self.monitoring_stats['total_records_processed'] += 1
                self.monitoring_stats['total_alarms_generated'] += len(record_alarms)
                self.monitoring_stats['last_processed_time'] = datetime.now()
                self.monitoring_stats['current_file_path'] = str(file_path)
                
        except Exception as e:
            self.logger.error(f"Failed to process file update: {e}")
    
    def _monitoring_worker(self, run_id: str):
        """
        Monitoring worker thread
        
        Parameters
        ----------
        run_id : str
            Run ID
        """
        try:
            if self.file_provider:
                self.file_provider.start()
                
                # Keep monitoring until stopped
                while not self.stop_monitoring_event.is_set():
                    self.stop_monitoring_event.wait(1)
                    
        except Exception as e:
            self.logger.error(f"Monitoring worker error: {e}")
        finally:
            if self.file_provider:
                self.file_provider.stop()
    
    def _handle_alarm(self, alarm: AlarmEvent):
        """
        Handle alarm event
        
        Parameters
        ----------
        alarm : AlarmEvent
            Alarm event to handle
        """
        try:
            # Call all registered handlers
            for handler in self.alarm_handlers:
                try:
                    handler(alarm)
                except Exception as e:
                    self.logger.error(f"Alarm handler error: {e}")
                    
        except Exception as e:
            self.logger.error(f"Failed to handle alarm: {e}")


def default_alarm_handler(alarm: AlarmEvent):
    """
    Default alarm handler
    
    Parameters
    ----------
    alarm : AlarmEvent
        Alarm event to handle
    """
    print(f"ALARM: {alarm.severity.value} - {alarm.description}") 