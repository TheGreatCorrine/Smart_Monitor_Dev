"""
backend/app/di/config.py
------------------------------------
Dependency Injection Configuration - Register all services
"""
from .container import container

from ..interfaces.IMonitorService import IMonitorService
from ..interfaces.IChannelConfigurationService import IChannelConfigurationService
from ..interfaces.IFileProvider import IFileProvider

from ..usecases.Monitor import MonitorService
from ..services.ChannelConfigurationService import ChannelConfigurationService
from ..services.SessionService import SessionService
from ..infra.fileprovider import SimulatedFileProvider, LocalFileProvider


def configure_dependencies():
    """
    Configure all dependencies in the DI container
    """
    # Register core services
    container.register(IMonitorService, MonitorService, singleton=True)
    container.register(IChannelConfigurationService, ChannelConfigurationService, singleton=True)
    container.register(SessionService, SessionService, singleton=True)
    
    # Register file providers (not singletons, create new instances as needed)
    container.register(IFileProvider, SimulatedFileProvider, singleton=False)
    
    # Note: LocalFileProvider can be registered separately if needed
    # container.register(IFileProvider, LocalFileProvider, singleton=False)


def get_monitor_service() -> IMonitorService:
    """
    Get monitor service instance
    
    Returns
    -------
    IMonitorService
        Monitor service instance
    """
    return container.resolve(IMonitorService)


def get_channel_service() -> IChannelConfigurationService:
    """
    Get channel configuration service instance
    
    Returns
    -------
    IChannelConfigurationService
        Channel configuration service instance
    """
    return container.resolve(IChannelConfigurationService)


def get_session_service() -> SessionService:
    """
    Get session service instance
    
    Returns
    -------
    SessionService
        Session service instance
    """
    return container.resolve(SessionService)


def create_file_provider(provider_type: str = "simulated", file_path: str = "data/test.dat") -> IFileProvider:
    """
    Create file provider instance
    
    Parameters
    ----------
    provider_type : str
        Type of file provider ("simulated" or "local")
    file_path : str
        File path for the provider
        
    Returns
    -------
    IFileProvider
        File provider instance
    """
    if provider_type == "local":
        return LocalFileProvider(file_path)
    else:
        return SimulatedFileProvider(file_path, "1")


# Configure dependencies when module is imported
configure_dependencies() 