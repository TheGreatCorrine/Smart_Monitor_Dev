"""
backend/app/infra/config/RuleLoader.py
------------------------------------
基础设施层：规则配置加载器，负责从YAML文件加载规则配置
"""
from __future__ import annotations

import yaml
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

from ...entities.Rule import Rule, Condition, ConditionType, Operator, Severity


@dataclass
class RuleConfig:
    """规则配置"""
    id: str
    name: str
    description: str
    conditions: List[Dict]
    severity: str
    enabled: bool = True


class RuleLoader:
    """规则配置加载器"""
    
    def __init__(self, config_path: str = "config/rules.yaml"):
        self.config_path = Path(config_path)
    
    def load_rules(self) -> List[Rule]:
        """
        从YAML文件加载规则配置
        
        Returns
        -------
        List[Rule]
            规则列表
        """
        if not self.config_path.exists():
            return []
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        rules = []
        for rule_config in config_data.get('rules', []):
            rule = self._parse_rule(rule_config)
            if rule:
                rules.append(rule)
        
        return rules
    
    def _parse_rule(self, config: Dict) -> Optional[Rule]:
        """解析单个规则配置"""
        try:
            conditions = []
            for cond_config in config.get('conditions', []):
                condition = self._parse_condition(cond_config)
                if condition:
                    conditions.append(condition)
            
            if not conditions:
                return None
            
            return Rule(
                id=config['id'],
                name=config['name'],
                description=config.get('description', ''),
                conditions=conditions,
                severity=Severity(config['severity']),
                enabled=config.get('enabled', True)
            )
        except (KeyError, ValueError) as e:
            print(f"解析规则配置失败: {e}")
            return None
    
    def _parse_condition(self, config: Dict) -> Optional[Condition]:
        """解析条件配置"""
        try:
            condition_type = ConditionType(config['type'])
            
            if condition_type in [ConditionType.LOGIC_AND, ConditionType.LOGIC_OR]:
                # 逻辑组合条件
                sub_conditions = []
                for sub_config in config.get('conditions', []):
                    sub_condition = self._parse_condition(sub_config)
                    if sub_condition:
                        sub_conditions.append(sub_condition)
                
                if not sub_conditions:
                    return None
                
                return Condition(
                    type=condition_type,
                    sensor="",  # 逻辑条件不需要传感器
                    operator=Operator.EQUAL,  # 占位符
                    conditions=sub_conditions
                )
            else:
                # 普通条件
                return Condition(
                    type=condition_type,
                    sensor=config['sensor'],
                    operator=Operator(config['operator']),
                    value=config.get('value'),
                    duration_minutes=config.get('duration_minutes')
                )
        except (KeyError, ValueError) as e:
            print(f"解析条件配置失败: {e}")
            return None 