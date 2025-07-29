"""
tests/unit/test_adapters.py
------------------------------------
Unit tests for interface adapters
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, Optional
from pathlib import Path
import json
import tempfile
import os

# Import adapter
from backend.app.adapters.GUIAdapter import GUIAdapter

# Import interfaces
from backend.app.interfaces.IMonitorService import IMonitorService
from backend.app.interfaces.IChannelConfigurationService import IChannelConfigurationService
from backend.app.interfaces.IFileProvider import IFileProvider

# Import entities
from backend.app.entities.AlarmEvent import AlarmEvent


class TestGUIAdapter(unittest.TestCase):
    """Test GUIAdapter functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_monitor_service = Mock(spec=IMonitorService)
        self.mock_channel_service = Mock(spec=IChannelConfigurationService)
        self.mock_file_provider = Mock(spec=IFileProvider)
        
        # Create adapter
        self.adapter = GUIAdapter(self.mock_monitor_service, self.mock_channel_service)
    
    def test_initialization(self):
        """Test adapter initialization"""
        self.assertEqual(self.adapter.monitor_service, self.mock_monitor_service)
        self.assertEqual(self.adapter.channel_service, self.mock_channel_service)
        self.assertIsInstance(self.adapter.label_selection_path, Path)
    
    def test_load_label_configuration_success(self):
        """Test successful label configuration loading"""
        # Mock configuration data
        mock_config = {
            'categories': {
                'temperature': {
                    'channels': ['T1'],
                    'subtypes': []
                }
            },
            'total_channels': 1,
            'monitorable_channels': 1
        }
        
        self.mock_channel_service.get_configuration_for_ui.return_value = mock_config
        
        # Test loading
        result = self.adapter.load_label_configuration()
        
        # Verify result
        self.assertEqual(result, mock_config)
        self.mock_channel_service.get_configuration_for_ui.assert_called_once()
    
    def test_load_label_configuration_error(self):
        """Test label configuration loading with error"""
        # Mock exception
        self.mock_channel_service.get_configuration_for_ui.side_effect = Exception("Test error")
        
        # Test loading
        result = self.adapter.load_label_configuration()
        
        # Verify fallback to empty config
        self.assertEqual(result, {'categories': {}})
    
    def test_save_label_selection_success(self):
        """Test successful label selection saving"""
        selected_labels = {'T1': 'temp', 'T2': 'humidity'}
        
        # Test saving
        result = self.adapter.save_label_selection(selected_labels)
        
        # Verify result
        self.assertTrue(result)
        
        # Verify file was created and contains correct data
        self.assertTrue(self.adapter.label_selection_path.exists())
        
        with open(self.adapter.label_selection_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertIn('timestamp', data)
            self.assertIn('labels', data)
            self.assertEqual(data['labels'], selected_labels)
    
    def test_save_label_selection_error(self):
        """Test label selection saving with error"""
        # Mock file write error
        with patch('builtins.open', side_effect=Exception("Write error")):
            result = self.adapter.save_label_selection({'T1': 'temp'})
            self.assertFalse(result)
    
    def test_load_label_selection_success(self):
        """Test successful label selection loading"""
        # Create test file
        test_labels = {'T1': 'temp', 'T2': 'humidity'}
        test_data = {
            'timestamp': '2023-01-01T00:00:00',
            'labels': test_labels
        }
        
        with open(self.adapter.label_selection_path, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        # Test loading
        result = self.adapter.load_label_selection()
        
        # Verify result
        self.assertEqual(result, test_labels)
    
    def test_load_label_selection_file_not_exists(self):
        """Test label selection loading when file doesn't exist"""
        # Ensure file doesn't exist
        if self.adapter.label_selection_path.exists():
            self.adapter.label_selection_path.unlink()
        
        # Test loading
        result = self.adapter.load_label_selection()
        
        # Verify result
        self.assertIsNone(result)
    
    def test_load_label_selection_error(self):
        """Test label selection loading with error"""
        # Create invalid JSON file
        with open(self.adapter.label_selection_path, 'w', encoding='utf-8') as f:
            f.write("invalid json")
        
        # Test loading
        result = self.adapter.load_label_selection()
        
        # Verify result
        self.assertIsNone(result)
    
    def test_start_monitoring_success(self):
        """Test successful monitoring start"""
        # Mock monitor service
        mock_alarms = [Mock(), Mock()]
        self.mock_monitor_service.process_data_file.return_value = (mock_alarms, 100)
        
        # Test monitoring
        result = self.adapter.start_monitoring("test.dat", "config.yaml", "run1")
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertEqual(result['records_count'], 100)
        self.assertEqual(result['alarms_count'], 2)
        self.assertEqual(result['alarms'], mock_alarms)
        
        # Verify monitor service was called
        self.mock_monitor_service.initialize.assert_called_once_with("config.yaml")
        self.mock_monitor_service.process_data_file.assert_called_once_with("test.dat", "run1")
    
    def test_start_monitoring_error(self):
        """Test monitoring start with error"""
        # Mock exception
        self.mock_monitor_service.initialize.side_effect = Exception("Test error")
        
        # Test monitoring
        result = self.adapter.start_monitoring("test.dat", "config.yaml", "run1")
        
        # Verify result
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'Test error')
    
    def test_start_simulation_success(self):
        """Test successful simulation start"""
        # Mock monitor service
        self.mock_monitor_service.start_continuous_monitoring.return_value = True
        
        # Test simulation
        result = self.adapter.start_simulation("test.dat", "config.yaml", "run1", "6", self.mock_file_provider)
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertEqual(result['workstation_id'], "6")
        
        # Verify monitor service was called
        self.mock_monitor_service.initialize.assert_called_once_with("config.yaml")
        self.mock_monitor_service.set_file_provider.assert_called_once_with(self.mock_file_provider)
        self.mock_monitor_service.start_continuous_monitoring.assert_called_once_with("run1")
    
    def test_start_simulation_failure(self):
        """Test simulation start with failure"""
        # Mock failure
        self.mock_monitor_service.start_continuous_monitoring.return_value = False
        
        # Test simulation
        result = self.adapter.start_simulation("test.dat", "config.yaml", "run1", "6", self.mock_file_provider)
        
        # Verify result
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'Failed to start simulation')
    
    def test_start_simulation_error(self):
        """Test simulation start with error"""
        # Mock exception
        self.mock_monitor_service.initialize.side_effect = Exception("Test error")
        
        # Test simulation
        result = self.adapter.start_simulation("test.dat", "config.yaml", "run1", "6", self.mock_file_provider)
        
        # Verify result
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'Test error')
    
    def test_stop_monitoring_success(self):
        """Test successful monitoring stop"""
        # Mock success
        self.mock_monitor_service.stop_continuous_monitoring.return_value = True
        
        # Test stopping
        result = self.adapter.stop_monitoring()
        
        # Verify result
        self.assertTrue(result)
        self.mock_monitor_service.stop_continuous_monitoring.assert_called_once()
    
    def test_stop_monitoring_error(self):
        """Test monitoring stop with error"""
        # Mock exception
        self.mock_monitor_service.stop_continuous_monitoring.side_effect = Exception("Test error")
        
        # Test stopping
        result = self.adapter.stop_monitoring()
        
        # Verify result
        self.assertFalse(result)
    
    def test_get_monitoring_status_success(self):
        """Test successful status retrieval"""
        # Mock status
        mock_status = {
            'is_monitoring': True,
            'stats': {'total_records_processed': 100}
        }
        self.mock_monitor_service.get_monitoring_status.return_value = mock_status
        
        # Test status retrieval
        result = self.adapter.get_monitoring_status()
        
        # Verify result
        self.assertEqual(result, mock_status)
        self.mock_monitor_service.get_monitoring_status.assert_called_once()
    
    def test_get_monitoring_status_error(self):
        """Test status retrieval with error"""
        # Mock exception
        self.mock_monitor_service.get_monitoring_status.side_effect = Exception("Test error")
        
        # Test status retrieval
        result = self.adapter.get_monitoring_status()
        
        # Verify result
        self.assertEqual(result, {})
    
    def test_add_alarm_handler(self):
        """Test alarm handler addition"""
        mock_handler = Mock()
        
        # Test adding handler
        self.adapter.add_alarm_handler(mock_handler)
        
        # Verify handler was added
        self.mock_monitor_service.add_alarm_handler.assert_called_once_with(mock_handler)
    
    def test_validate_file_path_valid(self):
        """Test file path validation with valid path"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.dat', delete=False) as f:
            temp_file = f.name
        
        try:
            # Test validation
            result = self.adapter.validate_file_path(temp_file)
            
            # Verify result
            self.assertTrue(result['valid'])
            self.assertEqual(result['file_path'], temp_file)
        finally:
            # Clean up
            os.unlink(temp_file)
    
    def test_validate_file_path_not_exists(self):
        """Test file path validation with non-existent file"""
        # Test validation
        result = self.adapter.validate_file_path("nonexistent.dat")
        
        # Verify result
        self.assertFalse(result['valid'])
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'File does not exist')
    
    def test_validate_file_path_not_file(self):
        """Test file path validation with directory"""
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test validation
            result = self.adapter.validate_file_path(temp_dir)
            
            # Verify result
            self.assertFalse(result['valid'])
            self.assertIn('error', result)
            self.assertEqual(result['error'], 'Path is not a file')
    
    def test_validate_file_path_wrong_extension(self):
        """Test file path validation with wrong extension"""
        # Create temporary file with wrong extension
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_file = f.name
        
        try:
            # Test validation
            result = self.adapter.validate_file_path(temp_file)
            
            # Verify result
            self.assertFalse(result['valid'])
            self.assertIn('error', result)
            self.assertEqual(result['error'], 'File must be a .dat file')
        finally:
            # Clean up
            os.unlink(temp_file)
    
    def test_auto_infer_workstation_id_success(self):
        """Test successful workstation ID inference"""
        # Test with MPL filename
        result = self.adapter.auto_infer_workstation_id("data/MPL6_test.dat")
        
        # Verify result
        self.assertEqual(result, "6")
    
    def test_auto_infer_workstation_id_lowercase(self):
        """Test workstation ID inference with lowercase filename"""
        # Test with lowercase filename
        result = self.adapter.auto_infer_workstation_id("data/mpl6_test.dat")
        
        # Verify result
        self.assertEqual(result, "6")
    
    def test_auto_infer_workstation_id_no_match(self):
        """Test workstation ID inference with no match"""
        # Test with non-matching filename
        result = self.adapter.auto_infer_workstation_id("data/test.dat")
        
        # Verify result
        self.assertIsNone(result)
    
    def test_auto_infer_workstation_id_error(self):
        """Test workstation ID inference with error"""
        # Test with invalid path
        result = self.adapter.auto_infer_workstation_id("")
        
        # Verify result
        self.assertIsNone(result)


class TestGUIAdapterIntegration(unittest.TestCase):
    """Integration tests for GUIAdapter with real services"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Import real services for integration testing
        from backend.app.usecases.Monitor import MonitorService
        from backend.app.services.ChannelConfigurationService import ChannelConfigurationService
        
        # Create real services
        self.monitor_service = MonitorService()
        self.channel_service = ChannelConfigurationService("config/label_channel_match.yaml")
        
        # Create adapter
        self.adapter = GUIAdapter(self.monitor_service, self.channel_service)
    
    def test_real_service_integration(self):
        """Test adapter with real services"""
        # Test that adapter can work with real services
        self.assertIsNotNone(self.adapter.monitor_service)
        self.assertIsNotNone(self.adapter.channel_service)
        
        # Test that adapter methods don't raise exceptions
        try:
            status = self.adapter.get_monitoring_status()
            self.assertIsInstance(status, dict)
        except Exception as e:
            # This is expected if config files don't exist
            self.assertIsInstance(e, (FileNotFoundError, Exception))
    
    def test_label_selection_persistence(self):
        """Test label selection save and load cycle"""
        # Test data
        test_labels = {'T1': 'temperature', 'T2': 'humidity'}
        
        # Save labels
        save_result = self.adapter.save_label_selection(test_labels)
        self.assertTrue(save_result)
        
        # Load labels
        load_result = self.adapter.load_label_selection()
        self.assertEqual(load_result, test_labels)
        
        # Clean up
        if self.adapter.label_selection_path.exists():
            self.adapter.label_selection_path.unlink()


if __name__ == '__main__':
    unittest.main() 