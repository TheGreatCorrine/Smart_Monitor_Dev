"""
backend/app/di/container.py
------------------------------------
Dependency Injection Container - Simple DI container for Clean Architecture
"""
from typing import Dict, Type, Any, Optional
from pathlib import Path


class Container:
    """
    Simple Dependency Injection Container
    
    Manages dependencies and provides dependency resolution
    """
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._singletons: Dict[Type, Any] = {}
    
    def register(self, interface: Type, implementation: Type, singleton: bool = False) -> None:
        """
        Register a service implementation
        
        Parameters
        ----------
        interface : Type
            Interface type
        implementation : Type
            Implementation type
        singleton : bool
            Whether to create singleton instances
        """
        self._services[interface] = implementation
        if singleton:
            self._singletons[interface] = None
    
    def register_instance(self, interface: Type, instance: Any) -> None:
        """
        Register a service instance
        
        Parameters
        ----------
        interface : Type
            Interface type
        instance : Any
            Service instance
        """
        self._services[interface] = lambda: instance
        self._singletons[interface] = instance
    
    def resolve(self, interface: Type) -> Any:
        """
        Resolve a service instance
        
        Parameters
        ----------
        interface : Type
            Interface type to resolve
            
        Returns
        -------
        Any
            Resolved service instance
            
        Raises
        ------
        KeyError
            If service is not registered
        """
        if interface not in self._services:
            raise KeyError(f"Service {interface.__name__} not registered")
        
        # Check if singleton already exists
        if interface in self._singletons and self._singletons[interface] is not None:
            return self._singletons[interface]
        
        # Create new instance
        implementation = self._services[interface]
        if callable(implementation):
            instance = implementation()
        else:
            instance = implementation
        
        # Store singleton if needed
        if interface in self._singletons:
            self._singletons[interface] = instance
        
        return instance
    
    def has(self, interface: Type) -> bool:
        """
        Check if service is registered
        
        Parameters
        ----------
        interface : Type
            Interface type to check
            
        Returns
        -------
        bool
            True if service is registered
        """
        return interface in self._services


# Global container instance
container = Container() 