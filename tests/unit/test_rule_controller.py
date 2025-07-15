"""
tests/unit/test_rule_controller.py
------------------------------------
规则控制器单元测试
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import List

from backend.app.controllers.RuleController import RuleController
from backend.app.entities.rule import Rule, Condition, ConditionType, Operator, Severity


class TestRuleController:
    """规则控制器测试类"""
    
    @pytest.fixture
    def mock_rule_loader(self):
        """模拟规则加载器"""
        loader = Mock()
        return loader
    
    @pytest.fixture
    def rule_controller(self, mock_rule_loader):
        """创建规则控制器实例"""
        return RuleController(mock_rule_loader)
    
    @pytest.fixture
    def sample_rules(self):
        """示例规则列表"""
        return [
            Rule(
                id="rule_001",
                name="高温告警",
                description="温度超过30度时告警",
                severity=Severity.HIGH,
                conditions=[
                    Condition(
                        type=ConditionType.THRESHOLD,
                        sensor="温度",
                        operator=Operator.GREATER_THAN,
                        value=30.0,
                        duration_minutes=1
                    )
                ],
                enabled=True
            ),
            Rule(
                id="rule_002",
                name="低温告警",
                description="温度低于10度时告警",
                severity=Severity.MEDIUM,
                conditions=[
                    Condition(
                        type=ConditionType.THRESHOLD,
                        sensor="温度",
                        operator=Operator.LESS_THAN,
                        value=10.0,
                        duration_minutes=2
                    )
                ],
                enabled=True
            )
        ]
    
    def test_load_rules_success(self, rule_controller, mock_rule_loader, sample_rules):
        """测试成功加载规则"""
        mock_rule_loader.load_rules.return_value = sample_rules
        
        result = rule_controller.load_rules()
        
        assert result['success'] is True
        assert result['data']['rules_count'] == 2
        assert len(result['data']['rules']) == 2
        
        # 验证第一个规则
        first_rule = result['data']['rules'][0]
        assert first_rule['id'] == "rule_001"
        assert first_rule['name'] == "高温告警"
        assert first_rule['severity'] == "high"
        assert len(first_rule['conditions']) == 1
        
        # 验证条件
        condition = first_rule['conditions'][0]
        assert condition['type'] == "threshold"
        assert condition['sensor'] == "温度"
        assert condition['operator'] == ">"
        assert condition['value'] == 30.0
    
    def test_load_rules_with_custom_path(self, rule_controller, sample_rules):
        """测试使用自定义路径加载规则"""
        with patch('backend.app.controllers.RuleController.RuleLoader') as mock_loader_class:
            mock_loader = Mock()
            mock_loader.load_rules.return_value = sample_rules
            mock_loader_class.return_value = mock_loader
            
            result = rule_controller.load_rules("custom/rules.yaml")
            
            assert result['success'] is True
            assert result['data']['rules_count'] == 2
            mock_loader_class.assert_called_once_with("custom/rules.yaml")
    
    def test_load_rules_exception(self, rule_controller, mock_rule_loader):
        """测试加载规则异常"""
        mock_rule_loader.load_rules.side_effect = Exception("加载错误")
        
        result = rule_controller.load_rules()
        
        assert result['success'] is False
        assert "加载错误" in result['error']
    
    def test_get_rule_success(self, rule_controller, mock_rule_loader, sample_rules):
        """测试成功获取单个规则"""
        mock_rule_loader.load_rules.return_value = sample_rules
        
        result = rule_controller.get_rule("rule_001")
        
        assert result['success'] is True
        assert result['data']['id'] == "rule_001"
        assert result['data']['name'] == "高温告警"
        assert result['data']['severity'] == "high"
    
    def test_get_rule_not_found(self, rule_controller, mock_rule_loader, sample_rules):
        """测试规则不存在"""
        mock_rule_loader.load_rules.return_value = sample_rules
        
        result = rule_controller.get_rule("nonexistent")
        
        assert result['success'] is False
        assert "规则不存在" in result['error']
    
    def test_get_rule_empty_id(self, rule_controller):
        """测试空ID参数"""
        result = rule_controller.get_rule("")
        
        assert result['success'] is False
        assert "规则ID不能为空" in result['error']
    
    def test_get_rule_exception(self, rule_controller, mock_rule_loader):
        """测试获取规则异常"""
        mock_rule_loader.load_rules.side_effect = Exception("获取错误")
        
        result = rule_controller.get_rule("rule_001")
        
        assert result['success'] is False
        assert "获取错误" in result['error']
    
    def test_get_rules_by_severity_success(self, rule_controller, mock_rule_loader, sample_rules):
        """测试成功按严重程度获取规则"""
        mock_rule_loader.load_rules.return_value = sample_rules
        
        result = rule_controller.get_rules_by_severity("high")
        
        assert result['success'] is True
        assert result['data']['severity'] == "high"
        assert result['data']['rules_count'] == 1
        assert len(result['data']['rules']) == 1
        assert result['data']['rules'][0]['id'] == "rule_001"
    
    def test_get_rules_by_severity_invalid(self, rule_controller):
        """测试无效严重程度"""
        result = rule_controller.get_rules_by_severity("invalid")
        
        assert result['success'] is False
        assert "无效的严重程度" in result['error']
    
    def test_get_rules_by_severity_exception(self, rule_controller, mock_rule_loader):
        """测试按严重程度获取规则异常"""
        mock_rule_loader.load_rules.side_effect = Exception("查询错误")
        
        result = rule_controller.get_rules_by_severity("high")
        
        assert result['success'] is False
        assert "查询错误" in result['error']
    
    def test_validate_rule_success(self, rule_controller):
        """测试成功验证规则"""
        rule_data = {
            "id": "test_rule",
            "name": "测试规则",
            "description": "测试描述",
            "severity": "high",
            "conditions": [
                {
                    "type": "threshold",
                    "sensor": "温度",
                    "operator": ">",
                    "value": 30.0,
                    "duration_minutes": 60
                }
            ]
        }
        
        result = rule_controller.validate_rule(rule_data)
        
        assert result['success'] is True
        assert "验证通过" in result['message']
    
    def test_validate_rule_missing_fields(self, rule_controller):
        """测试缺少必需字段"""
        rule_data = {
            "id": "test_rule",
            "name": "测试规则"
            # 缺少其他必需字段
        }
        
        result = rule_controller.validate_rule(rule_data)
        
        assert result['success'] is False
        assert "errors" in result
        assert len(result['errors']) > 0
    
    def test_validate_rule_invalid_severity(self, rule_controller):
        """测试无效严重程度"""
        rule_data = {
            "id": "test_rule",
            "name": "测试规则",
            "description": "测试描述",
            "severity": "invalid",
            "conditions": []
        }
        
        result = rule_controller.validate_rule(rule_data)
        
        assert result['success'] is False
        assert "无效的严重程度" in result['errors'][0]
    
    def test_validate_rule_invalid_conditions(self, rule_controller):
        """测试无效条件"""
        rule_data = {
            "id": "test_rule",
            "name": "测试规则",
            "description": "测试描述",
            "severity": "high",
            "conditions": "not_a_list"  # 应该是列表
        }
        
        result = rule_controller.validate_rule(rule_data)
        
        assert result['success'] is False
        assert "条件必须是非空列表" in result['errors'][0]
    
    def test_validate_rule_empty_conditions(self, rule_controller):
        """测试空条件列表"""
        rule_data = {
            "id": "test_rule",
            "name": "测试规则",
            "description": "测试描述",
            "severity": "high",
            "conditions": []
        }
        
        result = rule_controller.validate_rule(rule_data)
        
        assert result['success'] is False
        assert "条件必须是非空列表" in result['errors'][0]
    
    def test_validate_rule_invalid_condition_format(self, rule_controller):
        """测试无效条件格式"""
        rule_data = {
            "id": "test_rule",
            "name": "测试规则",
            "description": "测试描述",
            "severity": "high",
            "conditions": [
                "not_a_dict"  # 应该是字典
            ]
        }
        
        result = rule_controller.validate_rule(rule_data)
        
        assert result['success'] is False
        assert "条件 0 必须是字典" in result['errors'][0]
    
    def test_validate_rule_missing_condition_type(self, rule_controller):
        """测试条件缺少类型字段"""
        rule_data = {
            "id": "test_rule",
            "name": "测试规则",
            "description": "测试描述",
            "severity": "high",
            "conditions": [
                {
                    "sensor": "温度",
                    "operator": ">",
                    "value": 30.0
                    # 缺少 type 字段
                }
            ]
        }
        
        result = rule_controller.validate_rule(rule_data)
        
        assert result['success'] is False
        assert "条件 0 缺少类型字段" in result['errors'][0]
    
    def test_get_rule_statistics_success(self, rule_controller, mock_rule_loader, sample_rules):
        """测试成功获取规则统计"""
        mock_rule_loader.load_rules.return_value = sample_rules
        
        result = rule_controller.get_rule_statistics()
        
        assert result['success'] is True
        assert result['data']['total_rules'] == 2
        
        # 验证严重程度分布
        severity_dist = result['data']['severity_distribution']
        assert severity_dist['high'] == 1
        assert severity_dist['medium'] == 1
        assert severity_dist['low'] == 0
        assert severity_dist['critical'] == 0
        
        # 验证条件类型统计
        condition_types = result['data']['condition_types']
        assert condition_types['threshold'] == 2
    
    def test_get_rule_statistics_exception(self, rule_controller, mock_rule_loader):
        """测试获取规则统计异常"""
        mock_rule_loader.load_rules.side_effect = Exception("统计错误")
        
        result = rule_controller.get_rule_statistics()
        
        assert result['success'] is False
        assert "统计错误" in result['error']
    
    def test_format_rule(self, rule_controller, sample_rules):
        """测试规则格式化"""
        formatted = rule_controller._format_rule(sample_rules[0])
        
        assert formatted['id'] == "rule_001"
        assert formatted['name'] == "高温告警"
        assert formatted['description'] == "温度超过30度时告警"
        assert formatted['severity'] == "high"
        assert len(formatted['conditions']) == 1
        
        condition = formatted['conditions'][0]
        assert condition['type'] == "threshold"
        assert condition['sensor'] == "温度"
        assert condition['operator'] == ">"
        assert condition['value'] == 30.0
        assert condition['duration_minutes'] == 1 