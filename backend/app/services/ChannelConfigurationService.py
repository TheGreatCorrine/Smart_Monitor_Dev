"""
backend/app/services/ChannelConfigurationService.py
------------------------------------
Channel Configuration Service - Handles hierarchical channel configuration and user selection
"""
from __future__ import annotations

from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml
import logging

from ..entities.ChannelConfiguration import (
    ChannelCategory, ChannelSubtype, ChannelDefinition,
    UserChannelSelection, TestSessionChannelConfig
)
from ..interfaces.IChannelConfigurationService import IChannelConfigurationService


class ChannelConfigurationService(IChannelConfigurationService):
    """
    Channel Configuration Service
    
    Responsibilities:
    1. Load and parse channel configuration files
    2. Provide hierarchical channel configuration queries
    3. Manage user channel selections
    4. Generate frontend configuration interface data
    5. Validate user configuration legality
    """
    
    def __init__(self, config_path: str = "config/label_channel_match.yaml"):
        self.config_path = Path(config_path)
        self.logger = logging.getLogger(__name__)
        
        # Cache configuration data
        self._channel_definitions: Dict[str, ChannelDefinition] = {}
        self._categories_config: Dict[str, Dict] = {}
        self._loaded = False
    
    def load_configuration(self) -> None:
        """
        Load channel configuration file
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Channel configuration file does not exist: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            self._categories_config = config_data.get('channel_categories', {})
            self._build_channel_definitions()
            self._loaded = True
            
            self.logger.info(f"Successfully loaded {len(self._channel_definitions)} channel definitions")
            
        except Exception as e:
            self.logger.error(f"Failed to load channel configuration: {e}")
            raise
    
    def _build_channel_definitions(self) -> None:
        """
        Build ChannelDefinition objects based on configuration file
        """
        self._channel_definitions.clear()
        
        for category_key, category_config in self._categories_config.items():
            try:
                category = ChannelCategory(category_key)
                channels = category_config.get('channels', [])
                subtypes_config = category_config.get('subtypes', [])
                
                # Build subtype list
                subtypes = []
                default_subtype_id = None
                
                for subtype_config in subtypes_config:
                    subtype = ChannelSubtype(
                        subtype_id=subtype_config['subtype_id'],
                        label=subtype_config['label'],
                        tag=subtype_config['tag'],
                        description=subtype_config['description'],
                        unit=subtype_config.get('unit', ''),
                        typical_range=tuple(subtype_config['typical_range']) if subtype_config.get('typical_range') else None,
                        is_default=subtype_config.get('is_default', False)
                    )
                    subtypes.append(subtype)
                    
                    if subtype.is_default:
                        default_subtype_id = subtype.subtype_id
                
                # If no default, use the first one
                if not default_subtype_id and subtypes:
                    default_subtype_id = subtypes[0].subtype_id
                
                # Create definition for each channel
                for channel_id in channels:
                    self._channel_definitions[channel_id] = ChannelDefinition(
                        channel_id=channel_id,
                        category=category,
                        available_subtypes=subtypes,
                        default_subtype_id=default_subtype_id,
                        system_description=category_config.get('category_description', {}).get('en', ''),
                        is_monitorable=True
                    )
                    
            except Exception as e:
                self.logger.error(f"Failed to build channel definition for category {category_key}: {e}")
    
    def get_configuration_for_ui(self) -> Dict[str, Any]:
        """
        Get configuration data for UI display
        
        Returns
        -------
        Dict[str, Any]
            Configuration data structured for UI
        """
        if not self._loaded:
            self.load_configuration()
        
        # Organize data by category
        categories_data = {}
        
        for category_key, category_config in self._categories_config.items():
            if category_key in [cat.value for cat in ChannelCategory]:
                category_channels = []
                
                # Get all channels in this category
                for channel_id in category_config.get('channels', []):
                    if channel_id in self._channel_definitions:
                        definition = self._channel_definitions[channel_id]
                        
                        channel_data = {
                            'channel_id': channel_id,
                            'system_description': definition.system_description,
                            'available_subtypes': [
                                {
                                    'subtype_id': st.subtype_id,
                                    'label': st.label,
                                    'tag': st.tag,
                                    'description': st.description,
                                    'unit': st.unit,
                                    'typical_range': st.typical_range,
                                    'is_default': st.is_default
                                }
                                for st in definition.available_subtypes
                            ],
                            'default_subtype_id': definition.default_subtype_id
                        }
                        category_channels.append(channel_data)
                
                categories_data[category_key] = {
                    'category_name': category_config.get('category_name', {}),
                    'category_description': category_config.get('category_description', {}),
                    'channels': category_channels
                }
        
        return {
            'categories': categories_data,
            'total_channels': len(self._channel_definitions),
            'monitorable_channels': len([d for d in self._channel_definitions.values() if d.is_monitorable])
        }
    
    def get_default_user_configuration(self) -> Dict[str, Any]:
        """
        Get default user configuration
        
        Returns
        -------
        Dict[str, Any]
            Default configuration for users
        """
        if not self._loaded:
            self.load_configuration()
        
        default_config = {}
        
        for channel_id, definition in self._channel_definitions.items():
            if definition.is_monitorable:
                default_config[channel_id] = UserChannelSelection(
                    channel_id=channel_id,
                    selected_subtype_id=definition.default_subtype_id,
                    enabled=True
                )
        
        return default_config
    
    def validate_user_configuration(self, user_config: Dict[str, Any]) -> List[str]:
        """
        Validate user configuration legality
        
        Parameters
        ----------
        user_config : Dict[str, Any]
            User configuration
            
        Returns
        -------
        List[str]
            Validation error list, empty list means validation passed
        """
        if not self._loaded:
            self.load_configuration()
        
        errors = []
        
        for channel_id, selection in user_config.items():
            # Check if channel exists
            if channel_id not in self._channel_definitions:
                errors.append(f"Channel {channel_id} does not exist")
                continue
            
            definition = self._channel_definitions[channel_id]
            
            # Check if selected subtype exists
            selected_subtype_id = selection.get('selected_subtype_id', '')
            if selected_subtype_id:
                subtype_exists = any(st.subtype_id == selected_subtype_id 
                                   for st in definition.available_subtypes)
                if not subtype_exists:
                    errors.append(f"Subtype {selected_subtype_id} does not exist for channel {channel_id}")
        
        return errors
    
    def save_session_configuration(self, session_config: Dict[str, Any]) -> None:
        """
        Save session configuration
        
        Parameters
        ----------
        session_config : Dict[str, Any]
            Session configuration to save
        """
        # Implementation for saving session configuration
        # This could save to database or file
        pass
    
    def get_channel_label(self, session_id: str, channel_id: str) -> str:
        """
        Get channel label for a session
        
        Parameters
        ----------
        session_id : str
            Session ID
        channel_id : str
            Channel ID
            
        Returns
        -------
        str
            Channel label
        """
        if not self._loaded:
            self.load_configuration()
        
        if channel_id in self._channel_definitions:
            definition = self._channel_definitions[channel_id]
            return definition.default_subtype_id
        
        return channel_id 