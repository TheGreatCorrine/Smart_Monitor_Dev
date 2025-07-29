"""
tests/unit/test_dependency_injection.py
------------------------------------
Unit tests for dependency injection container
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, Type

# Import DI components
from backend.app.di.container import Container
from backend.app.di.config import configure_dependencies, get_monitor_service, get_channel_service, create_file_provider

# Import interfaces
from backend.app.interfaces.IMonitorService import IMonitorService
from backend.app.interfaces.IChannelConfigurationService import IChannelConfigurationService
from backend.app.interfaces.IFileProvider import IFileProvider

# Import implementations
from backend.app.usecases.Monitor import MonitorService
from backend.app.services.ChannelConfigurationService import ChannelConfigurationService
from backend.app.infra.fileprovider import SimulatedFileProvider, LocalFileProvider


class TestContainer(unittest.TestCase):
    """Test DI Container functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.container = Container()
    
    def test_register_service(self):
        """Test service registration"""
        # Test registration
        self.container.register(IMonitorService, MonitorService, singleton=True)
        
        # Verify registration
        self.assertTrue(self.container.has(IMonitorService))
    
    def test_register_instance(self):
        """Test instance registration"""
        mock_service = Mock(spec=IMonitorService)
        
        # Test registration
        self.container.register_instance(IMonitorService, mock_service)
        
        # Verify registration
        self.assertTrue(self.container.has(IMonitorService))
    
    def test_resolve_singleton(self):
        """Test singleton resolution"""
        # Register singleton
        self.container.register(IMonitorService, MonitorService, singleton=True)
        
        # Resolve first time
        instance1 = self.container.resolve(IMonitorService)
        
        # Resolve second time
        instance2 = self.container.resolve(IMonitorService)
        
        # Verify same instance returned
        self.assertIs(instance1, instance2)
        self.assertIsInstance(instance1, MonitorService)
    
    def test_resolve_factory(self):
        """Test factory resolution (non-singleton)"""
        # Register factory with lambda to provide constructor arguments
        self.container.register(IFileProvider, lambda: SimulatedFileProvider("data/test.dat", "1"), singleton=False)
        
        # Resolve first time
        instance1 = self.container.resolve(IFileProvider)
        
        # Resolve second time
        instance2 = self.container.resolve(IFileProvider)
        
        # Verify different instances returned
        self.assertIsNot(instance1, instance2)
        self.assertIsInstance(instance1, SimulatedFileProvider)
        self.assertIsInstance(instance2, SimulatedFileProvider)
    
    def test_resolve_registered_instance(self):
        """Test resolving registered instance"""
        mock_service = Mock(spec=IMonitorService)
        
        # Register instance
        self.container.register_instance(IMonitorService, mock_service)
        
        # Resolve
        instance = self.container.resolve(IMonitorService)
        
        # Verify same instance returned
        self.assertIs(instance, mock_service)
    
    def test_resolve_unregistered_service(self):
        """Test resolving unregistered service"""
        # Try to resolve unregistered service
        with self.assertRaises(KeyError):
            self.container.resolve(IMonitorService)
    
    def test_has_service(self):
        """Test has method"""
        # Initially should be False
        self.assertFalse(self.container.has(IMonitorService))
        
        # Register service
        self.container.register(IMonitorService, MonitorService)
        
        # Should be True
        self.assertTrue(self.container.has(IMonitorService))
    
    def test_register_multiple_services(self):
        """Test registering multiple services"""
        # Register multiple services
        self.container.register(IMonitorService, MonitorService, singleton=True)
        self.container.register(IChannelConfigurationService, ChannelConfigurationService, singleton=True)
        self.container.register(IFileProvider, lambda: SimulatedFileProvider("data/test.dat", "1"), singleton=False)
        
        # Verify all registered
        self.assertTrue(self.container.has(IMonitorService))
        self.assertTrue(self.container.has(IChannelConfigurationService))
        self.assertTrue(self.container.has(IFileProvider))
        
        # Verify can resolve all
        monitor = self.container.resolve(IMonitorService)
        channel = self.container.resolve(IChannelConfigurationService)
        file_provider = self.container.resolve(IFileProvider)
        
        self.assertIsInstance(monitor, MonitorService)
        self.assertIsInstance(channel, ChannelConfigurationService)
        self.assertIsInstance(file_provider, SimulatedFileProvider)


class TestDIConfiguration(unittest.TestCase):
    """Test DI configuration functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Clear any existing configuration
        from backend.app.di.config import container
        container._services.clear()
        container._singletons.clear()
    
    def test_configure_dependencies(self):
        """Test dependency configuration"""
        # Configure dependencies
        configure_dependencies()
        
        # Verify services are registered
        from backend.app.di.config import container
        self.assertTrue(container.has(IMonitorService))
        self.assertTrue(container.has(IChannelConfigurationService))
        self.assertTrue(container.has(IFileProvider))
    
    def test_get_monitor_service(self):
        """Test get_monitor_service function"""
        # Configure dependencies
        configure_dependencies()
        
        # Get service
        service = get_monitor_service()
        
        # Verify service
        self.assertIsInstance(service, MonitorService)
        self.assertIsInstance(service, IMonitorService)
    
    def test_get_channel_service(self):
        """Test get_channel_service function"""
        # Configure dependencies
        configure_dependencies()
        
        # Get service
        service = get_channel_service()
        
        # Verify service
        self.assertIsInstance(service, ChannelConfigurationService)
        self.assertIsInstance(service, IChannelConfigurationService)
    
    def test_create_file_provider_simulated(self):
        """Test create_file_provider with simulated type"""
        # Create simulated provider
        provider = create_file_provider("simulated", "data/test.dat")
        
        # Verify provider
        self.assertIsInstance(provider, SimulatedFileProvider)
        self.assertIsInstance(provider, IFileProvider)
    
    def test_create_file_provider_local(self):
        """Test create_file_provider with local type"""
        # Create local provider
        provider = create_file_provider("local", "data/test.dat")
        
        # Verify provider
        self.assertIsInstance(provider, LocalFileProvider)
        self.assertIsInstance(provider, IFileProvider)
    
    def test_create_file_provider_default(self):
        """Test create_file_provider with default type"""
        # Create default provider (should be simulated)
        provider = create_file_provider()
        
        # Verify provider
        self.assertIsInstance(provider, SimulatedFileProvider)
        self.assertIsInstance(provider, IFileProvider)
    
    def test_singleton_behavior(self):
        """Test singleton behavior across multiple calls"""
        # Configure dependencies
        configure_dependencies()
        
        # Get services multiple times
        service1 = get_monitor_service()
        service2 = get_monitor_service()
        service3 = get_channel_service()
        service4 = get_channel_service()
        
        # Verify singletons return same instance
        self.assertIs(service1, service2)
        self.assertIs(service3, service4)
        
        # Verify different services are different instances
        self.assertIsNot(service1, service3)
    
    def test_factory_behavior(self):
        """Test factory behavior for non-singleton services"""
        # Configure dependencies
        configure_dependencies()
        
        # Get file providers multiple times
        provider1 = create_file_provider("simulated", "data/test1.dat")
        provider2 = create_file_provider("simulated", "data/test2.dat")
        
        # Verify factory returns different instances
        self.assertIsNot(provider1, provider2)
        self.assertIsInstance(provider1, SimulatedFileProvider)
        self.assertIsInstance(provider2, SimulatedFileProvider)


class TestDIIntegration(unittest.TestCase):
    """Integration tests for DI with real services"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Configure dependencies
        configure_dependencies()
    
    def test_real_service_integration(self):
        """Test DI with real services"""
        # Get services
        monitor_service = get_monitor_service()
        channel_service = get_channel_service()
        file_provider = create_file_provider("simulated", "data/test.dat")
        
        # Verify services are properly initialized
        self.assertIsNotNone(monitor_service)
        self.assertIsNotNone(channel_service)
        self.assertIsNotNone(file_provider)
        
        # Verify services implement their interfaces
        self.assertIsInstance(monitor_service, IMonitorService)
        self.assertIsInstance(channel_service, IChannelConfigurationService)
        self.assertIsInstance(file_provider, IFileProvider)
    
    def test_service_methods_work(self):
        """Test that resolved services have working methods"""
        # Get services
        monitor_service = get_monitor_service()
        channel_service = get_channel_service()
        
        # Test monitor service methods
        self.assertTrue(hasattr(monitor_service, 'initialize'))
        self.assertTrue(hasattr(monitor_service, 'add_alarm_handler'))
        self.assertTrue(hasattr(monitor_service, 'get_monitoring_status'))
        
        # Test channel service methods
        self.assertTrue(hasattr(channel_service, 'get_configuration_for_ui'))
        self.assertTrue(hasattr(channel_service, 'validate_user_configuration'))
        self.assertTrue(hasattr(channel_service, 'get_channel_label'))
    
    def test_file_provider_methods_work(self):
        """Test that file provider has working methods"""
        # Get file provider
        file_provider = create_file_provider("simulated", "data/test.dat")
        
        # Test file provider methods
        self.assertTrue(hasattr(file_provider, 'set_callback'))
        self.assertTrue(hasattr(file_provider, 'start'))
        self.assertTrue(hasattr(file_provider, 'stop'))
        self.assertTrue(hasattr(file_provider, 'get_status'))
    
    def test_error_handling(self):
        """Test error handling in DI"""
        # Test resolving unregistered service
        container = Container()
        
        with self.assertRaises(KeyError):
            container.resolve(IMonitorService)
        
        # Test has method with unregistered service
        self.assertFalse(container.has(IMonitorService))


class TestDIPerformance(unittest.TestCase):
    """Performance tests for DI container"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.container = Container()
    
    def test_singleton_performance(self):
        """Test singleton resolution performance"""
        # Register singleton
        self.container.register(IMonitorService, MonitorService, singleton=True)
        
        # Resolve multiple times
        import time
        start_time = time.time()
        
        for _ in range(1000):
            service = self.container.resolve(IMonitorService)
        
        end_time = time.time()
        resolution_time = end_time - start_time
        
        # Verify performance is reasonable (should be very fast for singletons)
        self.assertLess(resolution_time, 1.0)  # Should complete in less than 1 second
    
    def test_factory_performance(self):
        """Test factory resolution performance"""
        # Register factory with lambda
        self.container.register(IFileProvider, lambda: SimulatedFileProvider("data/test.dat", "1"), singleton=False)
        
        # Resolve multiple times
        import time
        start_time = time.time()
        
        for _ in range(100):
            provider = self.container.resolve(IFileProvider)
        
        end_time = time.time()
        resolution_time = end_time - start_time
        
        # Verify performance is reasonable
        self.assertLess(resolution_time, 1.0)  # Should complete in less than 1 second


if __name__ == '__main__':
    unittest.main() 