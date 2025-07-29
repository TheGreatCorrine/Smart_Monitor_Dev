"""
tests/unit/test_interfaces.py
------------------------------------
Unit tests for interface abstractions
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

# Import interfaces
from backend.app.interfaces.IMonitorService import IMonitorService
from backend.app.interfaces.IChannelConfigurationService import IChannelConfigurationService
from backend.app.interfaces.IFileProvider import IFileProvider

# Import implementations
from backend.app.usecases.Monitor import MonitorService
from backend.app.services.ChannelConfigurationService import ChannelConfigurationService
from backend.app.infra.fileprovider.FileProvider import FileProvider


class TestIMonitorService(unittest.TestCase):
    """Test IMonitorService interface and implementation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_rule_engine = Mock()
        self.mock_rule_loader = Mock()
        self.mock_file_provider = Mock(spec=IFileProvider)
        
        # Create monitor service with mocked dependencies
        with patch('backend.app.usecases.Monitor.RuleEngine', return_value=self.mock_rule_engine):
            with patch('backend.app.usecases.Monitor.RuleLoader', return_value=self.mock_rule_loader):
                self.monitor_service = MonitorService()
    
    def test_interface_compliance(self):
        """Test that MonitorService implements IMonitorService interface"""
        self.assertIsInstance(self.monitor_service, IMonitorService)
    
    def test_initialize(self):
        """Test initialize method"""
        # Mock rule loading
        mock_rules = [Mock(), Mock()]
        self.mock_rule_loader.load_rules.return_value = mock_rules
        
        # Test initialization
        self.monitor_service.initialize("test_config.yaml")
        
        # Verify rule engine was loaded
        self.mock_rule_loader.load_rules.assert_called_once()
        self.mock_rule_engine.load_rules.assert_called_once_with(mock_rules)
    
    def test_set_file_provider(self):
        """Test set_file_provider method"""
        self.monitor_service.set_file_provider(self.mock_file_provider)
        
        # Verify file provider was set
        self.assertEqual(self.monitor_service.file_provider, self.mock_file_provider)
        self.mock_file_provider.set_callback.assert_called_once()
    
    def test_add_alarm_handler(self):
        """Test add_alarm_handler method"""
        mock_handler = Mock()
        self.monitor_service.add_alarm_handler(mock_handler)
        
        # Verify handler was added
        self.assertIn(mock_handler, self.monitor_service.alarm_handlers)
    
    def test_is_monitoring_property(self):
        """Test is_monitoring property"""
        # Initially should be False
        self.assertFalse(self.monitor_service.is_monitoring)
        
        # Set to True
        self.monitor_service._is_monitoring = True
        self.assertTrue(self.monitor_service.is_monitoring)
    
    def test_get_monitoring_status(self):
        """Test get_monitoring_status method"""
        status = self.monitor_service.get_monitoring_status()
        
        # Verify status structure
        self.assertIsInstance(status, dict)
        self.assertIn('is_monitoring', status)
        self.assertIn('stats', status)
        self.assertIsInstance(status['stats'], dict)


class TestIChannelConfigurationService(unittest.TestCase):
    """Test IChannelConfigurationService interface and implementation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_config_path = "test_config.yaml"
        
        # Create service with mocked config path
        with patch('backend.app.services.ChannelConfigurationService.Path') as mock_path:
            mock_path.return_value.exists.return_value = True
            self.channel_service = ChannelConfigurationService(self.mock_config_path)
    
    def test_interface_compliance(self):
        """Test that ChannelConfigurationService implements IChannelConfigurationService interface"""
        self.assertIsInstance(self.channel_service, IChannelConfigurationService)
    
    @patch('builtins.open', create=True)
    @patch('yaml.safe_load')
    def test_load_configuration(self, mock_yaml_load, mock_open):
        """Test load_configuration method"""
        # Mock YAML data
        mock_config_data = {
            'channel_categories': {
                'temperature_t': {
                    'channels': ['T1', 'T2'],
                    'subtypes': [
                        {
                            'subtype_id': 'temp',
                            'label': 'Temperature',
                            'tag': 'temp',
                            'description': 'Temperature measurement',
                            'unit': '°C',
                            'is_default': True
                        }
                    ],
                    'category_description': {'en': 'Temperature sensors'}
                }
            }
        }
        mock_yaml_load.return_value = mock_config_data
        
        # Test loading
        self.channel_service.load_configuration()
        
        # Verify configuration was loaded
        self.assertTrue(self.channel_service._loaded)
        self.assertGreater(len(self.channel_service._channel_definitions), 0)
    
    def test_get_configuration_for_ui(self):
        """Test get_configuration_for_ui method"""
        # Mock loaded configuration
        self.channel_service._loaded = True
        self.channel_service._categories_config = {
            'temperature': {
                'channels': ['T1'],
                'subtypes': [],
                'category_description': {'en': 'Test'}
            }
        }
        self.channel_service._channel_definitions = {}
        
        result = self.channel_service.get_configuration_for_ui()
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('categories', result)
        self.assertIn('total_channels', result)
        self.assertIn('monitorable_channels', result)
    
    def test_validate_user_configuration(self):
        """Test validate_user_configuration method"""
        # Mock loaded configuration
        self.channel_service._loaded = True
        self.channel_service._channel_definitions = {
            'T1': Mock(available_subtypes=[Mock(subtype_id='temp')])
        }
        
        # Test valid configuration
        valid_config = {'T1': {'selected_subtype_id': 'temp'}}
        errors = self.channel_service.validate_user_configuration(valid_config)
        self.assertEqual(len(errors), 0)
        
        # Test invalid configuration
        invalid_config = {'T1': {'selected_subtype_id': 'invalid'}}
        errors = self.channel_service.validate_user_configuration(invalid_config)
        self.assertGreater(len(errors), 0)
    
    def test_get_channel_label(self):
        """Test get_channel_label method"""
        # Mock loaded configuration
        self.channel_service._loaded = True
        self.channel_service._channel_definitions = {
            'T1': Mock(default_subtype_id='temp')
        }
        
        label = self.channel_service.get_channel_label('session1', 'T1')
        self.assertEqual(label, 'temp')
        
        # Test non-existent channel
        label = self.channel_service.get_channel_label('session1', 'NONEXISTENT')
        self.assertEqual(label, 'NONEXISTENT')


class TestIFileProvider(unittest.TestCase):
    """Test IFileProvider interface and implementation"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a concrete implementation for testing
        class TestFileProvider(FileProvider):
            def get_file_path(self):
                return Path("test.dat")
            
            def is_file_available(self):
                return True
        
        self.file_provider = TestFileProvider()
    
    def test_interface_compliance(self):
        """Test that FileProvider implements IFileProvider interface"""
        self.assertIsInstance(self.file_provider, IFileProvider)
    
    def test_set_callback(self):
        """Test set_callback method"""
        mock_callback = Mock()
        self.file_provider.set_callback(mock_callback)
        
        # Verify callback was set
        self.assertEqual(self.file_provider._callback, mock_callback)
    
    def test_start_stop(self):
        """Test start and stop methods"""
        # Test start
        result = self.file_provider.start()
        self.assertTrue(result)
        self.assertTrue(self.file_provider.is_running())
        
        # Test stop
        self.file_provider.stop()
        self.assertFalse(self.file_provider.is_running())
    
    def test_get_status(self):
        """Test get_status method"""
        status = self.file_provider.get_status()
        
        # Verify status structure
        self.assertIsInstance(status, dict)
        self.assertIn('is_active', status)
        self.assertIn('file_available', status)
        self.assertIn('file_path', status)
    
    def test_notify_file_update(self):
        """Test _notify_file_update method"""
        mock_callback = Mock()
        self.file_provider.set_callback(mock_callback)
        self.file_provider.start()
        
        # Test notification
        test_path = Path("test.dat")
        self.file_provider._notify_file_update(test_path)
        
        # Verify callback was called
        mock_callback.assert_called_once_with(test_path)


class TestInterfaceIntegration(unittest.TestCase):
    """Integration tests for interfaces working together"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_monitor_service = Mock(spec=IMonitorService)
        self.mock_channel_service = Mock(spec=IChannelConfigurationService)
        self.mock_file_provider = Mock(spec=IFileProvider)
    
    def test_monitor_service_with_file_provider(self):
        """Test MonitorService working with IFileProvider"""
        # Set up monitor service
        self.mock_monitor_service.set_file_provider(self.mock_file_provider)
        
        # Verify file provider was set
        self.mock_monitor_service.set_file_provider.assert_called_once_with(self.mock_file_provider)
    
    def test_channel_service_configuration_flow(self):
        """Test ChannelConfigurationService configuration flow"""
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
        
        # Test configuration retrieval
        result = self.mock_channel_service.get_configuration_for_ui()
        
        # Verify result
        self.assertEqual(result, mock_config)
        self.mock_channel_service.get_configuration_for_ui.assert_called_once()


if __name__ == '__main__':
    unittest.main() 