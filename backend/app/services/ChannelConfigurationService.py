"""
backend/app/services/ChannelConfigurationService.py
------------------------------------
Channel配置管理服务 - 处理分层channel配置和用户选择
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


class ChannelConfigurationService:
    """
    Channel配置管理服务
    
    职责：
    1. 加载和解析channel配置文件
    2. 提供分层的channel配置查询
    3. 管理用户的channel选择
    4. 生成前端配置界面数据
    5. 验证用户配置的合法性
    """
    
    def __init__(self, config_path: str = "config/label_channel_match.yaml"):
        self.config_path = Path(config_path)
        self.logger = logging.getLogger(__name__)
        
        # 缓存配置数据
        self._channel_definitions: Dict[str, ChannelDefinition] = {}
        self._categories_config: Dict[str, Dict] = {}
        self._loaded = False
    
    def load_configuration(self) -> None:
        """
        加载channel配置文件
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Channel配置文件不存在: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            self._categories_config = config_data.get('channel_categories', {})
            self._build_channel_definitions()
            self._loaded = True
            
            self.logger.info(f"成功加载了 {len(self._channel_definitions)} 个channel定义")
            
        except Exception as e:
            self.logger.error(f"加载channel配置失败: {e}")
            raise
    
    def _build_channel_definitions(self) -> None:
        """
        基于配置文件构建ChannelDefinition对象
        """
        self._channel_definitions.clear()
        
        for category_key, category_config in self._categories_config.items():
            try:
                category = ChannelCategory(category_key)
                channels = category_config.get('channels', [])
                subtypes_config = category_config.get('subtypes', [])
                
                # 构建细分类型列表
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
                
                # 如果没有默认值，使用第一个
                if not default_subtype_id and subtypes:
                    default_subtype_id = subtypes[0].subtype_id
                
                # 为每个channel创建定义
                for channel_id in channels:
                    self._channel_definitions[channel_id] = ChannelDefinition(
                        channel_id=channel_id,
                        category=category,
                        available_subtypes=subtypes.copy(),
                        default_subtype_id=default_subtype_id or "",
                        is_monitorable=True,
                        system_description=category_config.get('category_description', '')
                    )
                    
            except (KeyError, ValueError) as e:
                self.logger.warning(f"跳过无效的category配置 {category_key}: {e}")
    
    def get_configuration_for_ui(self) -> Dict[str, Any]:
        """
        获取用于前端UI的配置数据
        
        Returns
        -------
        Dict[str, Any]
            包含分类、channel和默认配置的完整数据
        """
        if not self._loaded:
            self.load_configuration()
        
        # 按大类组织数据
        categories_data = {}
        
        for category_key, category_config in self._categories_config.items():
            if category_key in [cat.value for cat in ChannelCategory]:
                category_channels = []
                
                # 获取该类别下的所有channel
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
                    'category_name': category_config.get('category_name', ''),
                    'category_description': category_config.get('category_description', ''),
                    'channels': category_channels
                }
        
        return {
            'categories': categories_data,
            'total_channels': len(self._channel_definitions),
            'monitorable_channels': len([d for d in self._channel_definitions.values() if d.is_monitorable])
        }
    
    def get_default_user_configuration(self) -> Dict[str, UserChannelSelection]:
        """
        获取默认的用户配置
        
        Returns
        -------
        Dict[str, UserChannelSelection]
            每个channel的默认选择
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
    
    def validate_user_configuration(self, user_config: Dict[str, UserChannelSelection]) -> List[str]:
        """
        验证用户配置的合法性
        
        Parameters
        ----------
        user_config : Dict[str, UserChannelSelection]
            用户配置
            
        Returns
        -------
        List[str]
            验证错误列表，空列表表示验证通过
        """
        if not self._loaded:
            self.load_configuration()
        
        errors = []
        
        for channel_id, selection in user_config.items():
            # 检查channel是否存在
            if channel_id not in self._channel_definitions:
                errors.append(f"未知的channel: {channel_id}")
                continue
            
            definition = self._channel_definitions[channel_id]
            
            # 检查选择的细分类型是否有效
            valid_subtypes = [st.subtype_id for st in definition.available_subtypes]
            if selection.selected_subtype_id not in valid_subtypes:
                errors.append(f"Channel {channel_id} 的细分类型 {selection.selected_subtype_id} 无效")
        
        return errors
    
    def save_session_configuration(self, session_config: TestSessionChannelConfig) -> None:
        """
        保存会话配置
        
        TODO: 实现持久化存储（数据库/文件）
        """
        # 验证配置
        errors = self.validate_user_configuration(session_config.selections)
        if errors:
            raise ValueError(f"配置验证失败: {'; '.join(errors)}")
        
        # TODO: 实现实际的保存逻辑
        self.logger.info(f"保存会话配置: {session_config.session_id}")
    
    def get_channel_label(self, session_id: str, channel_id: str) -> str:
        """
        获取指定session中channel的显示标签
        
        Parameters
        ----------
        session_id : str
            会话ID
        channel_id : str
            Channel ID
            
        Returns
        -------
        str
            显示标签
        """
        # TODO: 从持久化存储加载session配置
        # 这里返回默认标签作为示例
        if not self._loaded:
            self.load_configuration()
        
        if channel_id in self._channel_definitions:
            definition = self._channel_definitions[channel_id]
            for subtype in definition.available_subtypes:
                if subtype.subtype_id == definition.default_subtype_id:
                    return subtype.label
        
        return channel_id
    
    def get_available_subtypes(self, channel_id: str) -> List[ChannelSubtype]:
        """
        获取指定channel的可用细分类型
        """
        if not self._loaded:
            self.load_configuration()
        
        if channel_id in self._channel_definitions:
            return self._channel_definitions[channel_id].available_subtypes
        
        return [] 