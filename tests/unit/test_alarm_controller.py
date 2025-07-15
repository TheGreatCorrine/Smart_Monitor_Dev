"""
tests/unit/test_alarm_controller.py
------------------------------------
告警控制器单元测试
"""
import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime
from typing import List

from backend.app.controllers.AlarmController import AlarmController
from backend.app.entities.AlarmEvent import AlarmEvent, AlarmStatus
from backend.app.entities.rule import Severity
from backend.app.services.AlarmService import AlarmFilter


class TestAlarmController:
    """告警控制器测试类"""
    
    @pytest.fixture
    def mock_alarm_service(self):
        """模拟告警服务"""
        service = Mock()
        return service
    
    @pytest.fixture
    def alarm_controller(self, mock_alarm_service):
        """创建告警控制器实例"""
        return AlarmController(mock_alarm_service)
    
    @pytest.fixture
    def sample_alarm(self):
        """示例告警事件"""
        return AlarmEvent(
            id="ALARM_TEST_001",
            rule_id="test_rule",
            rule_name="测试规则",
            severity=Severity.HIGH,
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            description="测试告警",
            sensor_values={"温度": 25.5},
            run_id="test_run"
        )
    
    def test_list_alarms_success(self, alarm_controller, mock_alarm_service, sample_alarm):
        """测试成功列出告警"""
        # 准备
        mock_alarm_service.list_alarms.return_value = [sample_alarm]
        
        # 执行
        result = alarm_controller.list_alarms(severity="high")
        
        # 验证
        assert result['success'] is True
        assert len(result['data']['alarms']) == 1
        assert result['data']['count'] == 1
        assert result['data']['alarms'][0]['id'] == "ALARM_TEST_001"
        assert result['data']['alarms'][0]['severity'] == "high"
        
        # 验证服务调用
        mock_alarm_service.list_alarms.assert_called_once()
        call_args = mock_alarm_service.list_alarms.call_args[0][0]
        assert isinstance(call_args, AlarmFilter)
    
    def test_list_alarms_invalid_severity(self, alarm_controller):
        """测试无效严重程度参数"""
        result = alarm_controller.list_alarms(severity="invalid")
        
        assert result['success'] is False
        assert "无效的严重程度" in result['error']
    
    def test_list_alarms_invalid_status(self, alarm_controller):
        """测试无效状态参数"""
        result = alarm_controller.list_alarms(status="invalid")
        
        assert result['success'] is False
        assert "无效的状态" in result['error']
    
    def test_list_alarms_service_exception(self, alarm_controller, mock_alarm_service):
        """测试服务异常处理"""
        mock_alarm_service.list_alarms.side_effect = Exception("服务错误")
        
        result = alarm_controller.list_alarms()
        
        assert result['success'] is False
        assert "服务错误" in result['error']
    
    def test_get_alarm_success(self, alarm_controller, mock_alarm_service, sample_alarm):
        """测试成功获取单个告警"""
        mock_alarm_service.get_alarm.return_value = sample_alarm
        
        result = alarm_controller.get_alarm("ALARM_TEST_001")
        
        assert result['success'] is True
        assert result['data']['id'] == "ALARM_TEST_001"
        assert result['data']['rule_name'] == "测试规则"
        assert result['data']['severity'] == "high"
    
    def test_get_alarm_not_found(self, alarm_controller, mock_alarm_service):
        """测试告警不存在"""
        mock_alarm_service.get_alarm.return_value = None
        
        result = alarm_controller.get_alarm("NONEXISTENT")
        
        assert result['success'] is False
        assert "告警不存在" in result['error']
    
    def test_get_alarm_empty_id(self, alarm_controller):
        """测试空ID参数"""
        result = alarm_controller.get_alarm("")
        
        assert result['success'] is False
        assert "告警ID不能为空" in result['error']
    
    def test_acknowledge_alarm_success(self, alarm_controller, mock_alarm_service):
        """测试成功确认告警"""
        mock_alarm_service.acknowledge_alarm.return_value = True
        
        result = alarm_controller.acknowledge_alarm("ALARM_TEST_001", "admin")
        
        assert result['success'] is True
        assert "已确认" in result['message']
        mock_alarm_service.acknowledge_alarm.assert_called_once_with("ALARM_TEST_001", "admin")
    
    def test_acknowledge_alarm_failure(self, alarm_controller, mock_alarm_service):
        """测试确认告警失败"""
        mock_alarm_service.acknowledge_alarm.return_value = False
        
        result = alarm_controller.acknowledge_alarm("ALARM_TEST_001", "admin")
        
        assert result['success'] is False
        assert "确认告警失败" in result['error']
    
    def test_acknowledge_alarm_empty_params(self, alarm_controller):
        """测试空参数"""
        result = alarm_controller.acknowledge_alarm("", "admin")
        assert result['success'] is False
        
        result = alarm_controller.acknowledge_alarm("ALARM_TEST_001", "")
        assert result['success'] is False
    
    def test_resolve_alarm_success(self, alarm_controller, mock_alarm_service):
        """测试成功解决告警"""
        mock_alarm_service.resolve_alarm.return_value = True
        
        result = alarm_controller.resolve_alarm("ALARM_TEST_001", "admin")
        
        assert result['success'] is True
        assert "已解决" in result['message']
        mock_alarm_service.resolve_alarm.assert_called_once_with("ALARM_TEST_001", "admin")
    
    def test_resolve_alarm_failure(self, alarm_controller, mock_alarm_service):
        """测试解决告警失败"""
        mock_alarm_service.resolve_alarm.return_value = False
        
        result = alarm_controller.resolve_alarm("ALARM_TEST_001", "admin")
        
        assert result['success'] is False
        assert "解决告警失败" in result['error']
    
    def test_get_alarm_statistics_success(self, alarm_controller, mock_alarm_service):
        """测试成功获取告警统计"""
        mock_stats = {
            "total_alarms": 10,
            "active_alarms": 5,
            "acknowledged_alarms": 3,
            "resolved_alarms": 2
        }
        mock_alarm_service.get_alarm_statistics.return_value = mock_stats
        
        result = alarm_controller.get_alarm_statistics()
        
        assert result['success'] is True
        assert result['data'] == mock_stats
    
    def test_get_alarm_statistics_exception(self, alarm_controller, mock_alarm_service):
        """测试获取统计异常"""
        mock_alarm_service.get_alarm_statistics.side_effect = Exception("统计错误")
        
        result = alarm_controller.get_alarm_statistics()
        
        assert result['success'] is False
        assert "统计错误" in result['error']
    
    def test_format_alarm(self, alarm_controller, sample_alarm):
        """测试告警格式化"""
        formatted = alarm_controller._format_alarm(sample_alarm)
        
        assert formatted['id'] == "ALARM_TEST_001"
        assert formatted['rule_id'] == "test_rule"
        assert formatted['rule_name'] == "测试规则"
        assert formatted['severity'] == "high"
        assert formatted['status'] == "active"
        assert formatted['sensor_values'] == {"温度": 25.5}
        assert formatted['run_id'] == "test_run" 