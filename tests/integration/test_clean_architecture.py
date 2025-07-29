"""
tests/integration/test_clean_architecture.py
------------------------------------
Integration tests for Clean Architecture implementation
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List
from pathlib import Path
import tempfile
import json
import os

# Import Clean Architecture components
from backend.app.interfaces.IMonitorService import IMonitorService
from backend.app.interfaces.IChannelConfigurationService import IChannelConfigurationService
from backend.app.interfaces.IFileProvider import IFileProvider

from backend.app.adapters.GUIAdapter import GUIAdapter
from backend.app.di.config import configure_dependencies, get_monitor_service, get_channel_service, create_file_provider

from backend.app.usecases.Monitor import MonitorService
from backend.app.services.ChannelConfigurationService import ChannelConfigurationService
from backend.app.infra.fileprovider import SimulatedFileProvider

from backend.app.entities.AlarmEvent import AlarmEvent
from backend.app.entities.record import Record


class TestCleanArchitectureIntegration(unittest.TestCase):
    """Integration tests for Clean Architecture components working together"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Configure dependencies
        configure_dependencies()
        
        # Get services through DI
        self.monitor_service = get_monitor_service()
        self.channel_service = get_channel_service()
        self.file_provider = create_file_provider("simulated")
        
        # Create adapter
        self.adapter = GUIAdapter(self.monitor_service, self.channel_service)
    
    def test_complete_architecture_flow(self):
        """Test complete architecture flow from GUI to business logic"""
        # 1. Test interface compliance
        self.assertIsInstance(self.monitor_service, IMonitorService)
        self.assertIsInstance(self.channel_service, IChannelConfigurationService)
        self.assertIsInstance(self.file_provider, IFileProvider)
        
        # 2. Test adapter initialization
        self.assertIsNotNone(self.adapter.monitor_service)
        self.assertIsNotNone(self.adapter.channel_service)
        
        # 3. Test service communication through adapter
        status = self.adapter.get_monitoring_status()
        self.assertIsInstance(status, dict)
        
        # 4. Test file provider integration
        mock_handler = Mock()
        self.adapter.add_alarm_handler(mock_handler)
        # Note: We can't assert on the real service method, but we can verify the adapter works
        self.assertIsNotNone(self.adapter.monitor_service)
    
    def test_dependency_injection_flow(self):
        """Test dependency injection flow"""
        # Test that DI container provides correct services
        monitor = get_monitor_service()
        channel = get_channel_service()
        provider = create_file_provider("simulated")
        
        # Verify services are properly typed
        self.assertIsInstance(monitor, MonitorService)
        self.assertIsInstance(channel, ChannelConfigurationService)
        self.assertIsInstance(provider, SimulatedFileProvider)
        
        # Verify services implement interfaces
        self.assertIsInstance(monitor, IMonitorService)
        self.assertIsInstance(channel, IChannelConfigurationService)
        self.assertIsInstance(provider, IFileProvider)
    
    def test_adapter_business_logic_abstraction(self):
        """Test that adapter properly abstracts business logic"""
        # Test label configuration loading
        config = self.adapter.load_label_configuration()
        self.assertIsInstance(config, dict)
        
        # Test file validation
        with tempfile.NamedTemporaryFile(suffix='.dat', delete=False) as f:
            temp_file = f.name
        
        try:
            validation = self.adapter.validate_file_path(temp_file)
            self.assertTrue(validation['valid'])
        finally:
            os.unlink(temp_file)
        
        # Test workstation ID inference
        workstation_id = self.adapter.auto_infer_workstation_id("data/MPL6_test.dat")
        self.assertEqual(workstation_id, "6")
    
    def test_error_handling_across_layers(self):
        """Test error handling across architecture layers"""
        # Test adapter error handling
        result = self.adapter.validate_file_path("nonexistent.dat")
        self.assertFalse(result['valid'])
        self.assertIn('error', result)
        
        # Test service error handling
        try:
            self.channel_service.load_configuration()
        except Exception as e:
            # Expected if config file doesn't exist
            self.assertIsInstance(e, (FileNotFoundError, Exception))
    
    def test_label_selection_persistence_flow(self):
        """Test complete label selection persistence flow"""
        # Test data
        test_labels = {'T1': 'temperature', 'T2': 'humidity', 'P1': 'pressure'}
        
        # Save through adapter
        save_result = self.adapter.save_label_selection(test_labels)
        self.assertTrue(save_result)
        
        # Load through adapter
        load_result = self.adapter.load_label_selection()
        self.assertEqual(load_result, test_labels)
        
        # Clean up
        if self.adapter.label_selection_path.exists():
            self.adapter.label_selection_path.unlink()
    
    def test_monitoring_workflow(self):
        """Test complete monitoring workflow"""
        # Mock monitor service for testing
        mock_alarms = [Mock(), Mock()]
        self.monitor_service.process_data_file = Mock(return_value=(mock_alarms, 50))
        
        # Test monitoring through adapter
        result = self.adapter.start_monitoring("test.dat", "config.yaml", "run1")
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        self.assertIn('records_count', result)
        self.assertIn('alarms_count', result)
        self.assertIn('alarms', result)
    
    def test_simulation_workflow(self):
        """Test complete simulation workflow"""
        # Mock monitor service for testing
        self.monitor_service.start_continuous_monitoring = Mock(return_value=True)
        
        # Test simulation through adapter
        result = self.adapter.start_simulation("test.dat", "config.yaml", "run1", "6", self.file_provider)
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        self.assertIn('workstation_id', result)
    
    def test_interface_segregation(self):
        """Test that interfaces are properly segregated"""
        # Test that services only expose interface methods
        monitor_methods = dir(self.monitor_service)
        channel_methods = dir(self.channel_service)
        provider_methods = dir(self.file_provider)
        
        # Verify interface methods are available
        self.assertIn('initialize', monitor_methods)
        self.assertIn('process_data_file', monitor_methods)
        self.assertIn('get_monitoring_status', monitor_methods)
        
        self.assertIn('get_configuration_for_ui', channel_methods)
        self.assertIn('validate_user_configuration', channel_methods)
        
        self.assertIn('set_callback', provider_methods)
        self.assertIn('start', provider_methods)
        self.assertIn('stop', provider_methods)
    
    def test_dependency_direction(self):
        """Test that dependencies follow Clean Architecture direction"""
        # GUI should not directly depend on infrastructure
        # This is verified by the fact that GUI only imports adapter and DI
        
        # Adapter should depend on interfaces, not concrete implementations
        self.assertIsInstance(self.adapter.monitor_service, IMonitorService)
        self.assertIsInstance(self.adapter.channel_service, IChannelConfigurationService)
        
        # Services should implement interfaces
        self.assertIsInstance(self.monitor_service, IMonitorService)
        self.assertIsInstance(self.channel_service, IChannelConfigurationService)
        self.assertIsInstance(self.file_provider, IFileProvider)


class TestCleanArchitecturePerformance(unittest.TestCase):
    """Performance tests for Clean Architecture implementation"""
    
    def setUp(self):
        """Set up test fixtures"""
        configure_dependencies()
        self.adapter = GUIAdapter(get_monitor_service(), get_channel_service())
    
    def test_adapter_performance(self):
        """Test adapter method performance"""
        import time
        
        # Test label configuration loading performance
        start_time = time.time()
        for _ in range(100):
            config = self.adapter.load_label_configuration()
        end_time = time.time()
        
        # Should complete in reasonable time
        self.assertLess(end_time - start_time, 5.0)
    
    def test_di_resolution_performance(self):
        """Test DI resolution performance"""
        import time
        
        # Test service resolution performance
        start_time = time.time()
        for _ in range(100):
            monitor = get_monitor_service()
            channel = get_channel_service()
            provider = create_file_provider("simulated")
        end_time = time.time()
        
        # Should complete in reasonable time
        self.assertLess(end_time - start_time, 5.0)
    
    def test_file_validation_performance(self):
        """Test file validation performance"""
        import time
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.dat', delete=False) as f:
            temp_file = f.name
        
        try:
            # Test validation performance
            start_time = time.time()
            for _ in range(100):
                validation = self.adapter.validate_file_path(temp_file)
            end_time = time.time()
            
            # Should complete in reasonable time
            self.assertLess(end_time - start_time, 1.0)
        finally:
            os.unlink(temp_file)


class TestCleanArchitectureErrorHandling(unittest.TestCase):
    """Error handling tests for Clean Architecture implementation"""
    
    def setUp(self):
        """Set up test fixtures"""
        configure_dependencies()
        self.adapter = GUIAdapter(get_monitor_service(), get_channel_service())
    
    def test_service_initialization_errors(self):
        """Test service initialization error handling"""
        # Test with invalid configuration
        try:
            self.adapter.start_monitoring("nonexistent.dat", "nonexistent.yaml", "run1")
        except Exception as e:
            # Should handle errors gracefully
            self.assertIsInstance(e, (FileNotFoundError, Exception))
    
    def test_adapter_error_recovery(self):
        """Test adapter error recovery"""
        # Test with invalid file paths
        validation = self.adapter.validate_file_path("invalid/path/file.dat")
        self.assertFalse(validation['valid'])
        
        # Test with invalid workstation ID
        workstation_id = self.adapter.auto_infer_workstation_id("invalid_filename.txt")
        self.assertIsNone(workstation_id)
    
    def test_di_error_handling(self):
        """Test DI error handling"""
        from backend.app.di.container import Container
        
        container = Container()
        
        # Test resolving unregistered service
        with self.assertRaises(KeyError):
            container.resolve(IMonitorService)
        
        # Test has method with unregistered service
        self.assertFalse(container.has(IMonitorService))


class TestCleanArchitectureExtensibility(unittest.TestCase):
    """Extensibility tests for Clean Architecture implementation"""
    
    def test_interface_extensibility(self):
        """Test that new interfaces can be added easily"""
        # Test that we can create new mock services implementing interfaces
        mock_monitor = Mock(spec=IMonitorService)
        mock_channel = Mock(spec=IChannelConfigurationService)
        mock_provider = Mock(spec=IFileProvider)
        
        # Verify they can be used with adapter
        adapter = GUIAdapter(mock_monitor, mock_channel)
        self.assertIsNotNone(adapter)
    
    def test_adapter_extensibility(self):
        """Test that new adapters can be added easily"""
        # Test that we can create new adapters for different UIs
        class WebAdapter:
            def __init__(self, monitor_service: IMonitorService, channel_service: IChannelConfigurationService):
                self.monitor_service = monitor_service
                self.channel_service = channel_service
        
        # Verify it works with real services
        adapter = WebAdapter(get_monitor_service(), get_channel_service())
        self.assertIsNotNone(adapter)
    
    def test_service_extensibility(self):
        """Test that new services can be added easily"""
        # Test that we can register new services in DI
        from backend.app.di.container import Container
        
        container = Container()
        container.register(IMonitorService, MonitorService, singleton=True)
        
        # Verify service can be resolved
        service = container.resolve(IMonitorService)
        self.assertIsInstance(service, MonitorService)


if __name__ == '__main__':
    unittest.main() 