"""
backend/app/controllers/RuleController.py
------------------------------------
规则控制器 - 处理规则相关的用户请求
负责规则加载、查询、验证等功能
"""
from __future__ import annotations

from typing import Dict, Any, Optional, List
import logging

from ..entities.rule import Rule, Severity
from ..infra.config.RuleLoader import RuleLoader


class RuleController:
    """
    规则控制器
    
    职责：
    1. 处理规则加载请求
    2. 处理规则查询请求
    3. 提供规则验证功能
    4. 格式化规则输出
    """
    
    def __init__(self, rule_loader: Optional[RuleLoader] = None):
        self.rule_loader = rule_loader or RuleLoader('config/rules.yaml')
        self.logger = logging.getLogger(__name__)
    
    def load_rules(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        加载规则
        
        Parameters
        ----------
        config_path : str, optional
            配置文件路径
            
        Returns
        -------
        Dict[str, Any]
            加载结果
        """
        try:
            # 使用指定的配置路径或默认路径
            loader = RuleLoader(config_path) if config_path else self.rule_loader
            rules = loader.load_rules()
            
            # 格式化结果
            return {
                'success': True,
                'data': {
                    'rules_count': len(rules),
                    'rules': [self._format_rule(rule) for rule in rules]
                }
            }
            
        except Exception as e:
            self.logger.error(f"加载规则失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_rule(self, rule_id: str) -> Dict[str, Any]:
        """
        获取单个规则
        
        Parameters
        ----------
        rule_id : str
            规则ID
            
        Returns
        -------
        Dict[str, Any]
            规则信息
        """
        try:
            # 验证输入
            if not rule_id:
                raise ValueError("规则ID不能为空")
            
            # 加载规则
            rules = self.rule_loader.load_rules()
            
            # 查找指定规则
            rule = next((r for r in rules if r.id == rule_id), None)
            
            if not rule:
                return {
                    'success': False,
                    'error': f"规则不存在: {rule_id}"
                }
            
            # 格式化结果
            return {
                'success': True,
                'data': self._format_rule(rule)
            }
            
        except Exception as e:
            self.logger.error(f"获取规则失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_rules_by_severity(self, severity: str) -> Dict[str, Any]:
        """
        按严重程度获取规则
        
        Parameters
        ----------
        severity : str
            严重程度
            
        Returns
        -------
        Dict[str, Any]
            规则列表
        """
        try:
            # 验证严重程度
            if severity not in ['low', 'medium', 'high', 'critical']:
                return {
                    'success': False,
                    'error': f"无效的严重程度: {severity}"
                }
            
            # 加载规则
            rules = self.rule_loader.load_rules()
            
            # 过滤规则
            filtered_rules = [r for r in rules if r.severity.value == severity]
            
            # 格式化结果
            return {
                'success': True,
                'data': {
                    'severity': severity,
                    'rules_count': len(filtered_rules),
                    'rules': [self._format_rule(rule) for rule in filtered_rules]
                }
            }
            
        except Exception as e:
            self.logger.error(f"按严重程度获取规则失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_rule(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证规则数据
        
        Parameters
        ----------
        rule_data : Dict[str, Any]
            规则数据
            
        Returns
        -------
        Dict[str, Any]
            验证结果
        """
        try:
            errors = []
            
            # 验证必需字段
            required_fields = ['id', 'name', 'description', 'severity', 'conditions']
            for field in required_fields:
                if field not in rule_data:
                    errors.append(f"缺少必需字段: {field}")
            
            # 验证严重程度
            if 'severity' in rule_data:
                severity = rule_data['severity']
                if severity not in ['low', 'medium', 'high', 'critical']:
                    errors.append(f"无效的严重程度: {severity}")
            
            # 验证条件
            if 'conditions' in rule_data:
                conditions = rule_data['conditions']
                if not isinstance(conditions, list) or len(conditions) == 0:
                    errors.append("条件必须是非空列表")
                else:
                    for i, condition in enumerate(conditions):
                        if not isinstance(condition, dict):
                            errors.append(f"条件 {i} 必须是字典")
                        elif 'type' not in condition:
                            errors.append(f"条件 {i} 缺少类型字段")
            
            if errors:
                return {
                    'success': False,
                    'errors': errors
                }
            else:
                return {
                    'success': True,
                    'message': '规则数据验证通过'
                }
                
        except Exception as e:
            self.logger.error(f"验证规则失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_rule_statistics(self) -> Dict[str, Any]:
        """
        获取规则统计信息
        
        Returns
        -------
        Dict[str, Any]
            统计信息
        """
        try:
            rules = self.rule_loader.load_rules()
            
            # 按严重程度统计
            severity_stats = {}
            for severity in ['low', 'medium', 'high', 'critical']:
                count = len([r for r in rules if r.severity.value == severity])
                severity_stats[severity] = count
            
            # 按条件类型统计
            condition_types = {}
            for rule in rules:
                for condition in rule.conditions:
                    cond_type = condition.type.value
                    condition_types[cond_type] = condition_types.get(cond_type, 0) + 1
            
            return {
                'success': True,
                'data': {
                    'total_rules': len(rules),
                    'severity_distribution': severity_stats,
                    'condition_types': condition_types
                }
            }
            
        except Exception as e:
            self.logger.error(f"获取规则统计失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _format_rule(self, rule: Rule) -> Dict[str, Any]:
        """格式化规则"""
        return {
            'id': rule.id,
            'name': rule.name,
            'description': rule.description,
            'severity': rule.severity.value,
            'conditions': [
                {
                    'type': condition.type.value,
                    'sensor': condition.sensor,
                    'operator': condition.operator.value,
                    'value': condition.value,
                    'duration_minutes': condition.duration_minutes
                }
                for condition in rule.conditions
            ]
        } 