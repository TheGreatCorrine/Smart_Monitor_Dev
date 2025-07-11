"""
tests/unit/test_monitor_controller.py
------------------------------------
监控控制器单元测试
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from pathlib import Path

from backend.app.controllers.MonitorController import MonitorController
from backend.app.entities.Record import Record
from backend.app.entities.AlarmEvent import AlarmEvent
from backend.app.entities.Rule import Severity


class TestMonitorController:
    """监控控制器测试类"""
    
    @pytest.fixture
    def mock_monitor_service(self):
        service = Mock()
        service.alarm_handlers = []
        return service
    
    @pytest.fixture
    def monitor_controller(self, mock_monitor_service):
        return MonitorController(mock_monitor_service)
    
    @pytest.fixture
    def sample_record(self):
        return Record(
            run_id="test_run",
            ts=datetime(2024, 1, 1, 12, 0, 0),
            metrics={"温度": 25.5, "湿度": 60.0},
            file_pos=1000
        )
    
    @pytest.fixture
    def sample_alarm(self):
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
    
    def test_process_data_file_success(self, monitor_controller, mock_monitor_service, sample_alarm):
        mock_monitor_service.process_data_file.return_value = ([sample_alarm], 1000)
        with patch.object(monitor_controller, '_validate_file_path', return_value=True):
            result = monitor_controller.process_data_file("data/test.dat", "test_run")
        assert result['success'] is True
        assert result['data']['file_path'] == "data/test.dat"
        assert result['data']['run_id'] == "test_run"
        assert result['data']['records_count'] == 1000
        assert result['data']['alarms_count'] == 1
        assert len(result['data']['alarms']) == 1
        mock_monitor_service.process_data_file.assert_called_once_with("data/test.dat", "test_run")
    
    def test_process_data_file_invalid_path(self, monitor_controller):
        # 不mock，走真实分支
        result = monitor_controller.process_data_file("nonexistent.dat", "test_run")
        assert result['success'] is False
        assert "文件不存在或格式错误" in result['error']
    
    def test_process_data_file_service_exception(self, monitor_controller, mock_monitor_service):
        mock_monitor_service.process_data_file.side_effect = Exception("处理错误")
        with patch.object(monitor_controller, '_validate_file_path', return_value=True):
            result = monitor_controller.process_data_file("data/test.dat", "test_run")
        assert result['success'] is False
        assert "处理错误" in result['error']
    
    def test_process_record_success(self, monitor_controller, mock_monitor_service, sample_record, sample_alarm):
        mock_monitor_service.process_record.return_value = [sample_alarm]
        result = monitor_controller.process_record(sample_record, "test_run")
        assert result['success'] is True
        assert result['data']['run_id'] == "test_run"
        assert result['data']['alarms_count'] == 1
        assert len(result['data']['alarms']) == 1
        assert result['data']['timestamp'] == sample_record.ts.isoformat()
        mock_monitor_service.process_record.assert_called_once_with(sample_record, "test_run")
    
    def test_process_record_service_exception(self, monitor_controller, mock_monitor_service, sample_record):
        mock_monitor_service.process_record.side_effect = Exception("记录处理错误")
        result = monitor_controller.process_record(sample_record, "test_run")
        assert result['success'] is False
        assert "记录处理错误" in result['error']
    
    def test_get_monitor_status_success(self, monitor_controller, mock_monitor_service):
        mock_monitor_service.get_rule_summary.return_value = {
            "total_rules": 6,
            "severity_distribution": {"high": 3, "medium": 2, "low": 1}
        }
        mock_monitor_service.alarm_handlers = [Mock(), Mock()]
        result = monitor_controller.get_monitor_status()
        assert result['success'] is True
        assert result['data']['status'] == "active"
        assert result['data']['rules']['total_rules'] == 6
        assert result['data']['alarm_handlers_count'] == 2
    
    def test_get_monitor_status_exception(self, monitor_controller, mock_monitor_service):
        mock_monitor_service.get_rule_summary.side_effect = Exception("状态获取错误")
        result = monitor_controller.get_monitor_status()
        assert result['success'] is False
        assert "状态获取错误" in result['error']
    
    def test_add_alarm_handler_success(self, monitor_controller, mock_monitor_service):
        def test_handler(alarm):
            pass
        result = monitor_controller.add_alarm_handler("test_handler", test_handler)
        assert result['success'] is True
        assert "添加成功" in result['message']
        mock_monitor_service.add_alarm_handler.assert_called_once_with(test_handler)
    
    def test_add_alarm_handler_empty_name(self, monitor_controller):
        def test_handler(alarm):
            pass
        result = monitor_controller.add_alarm_handler("", test_handler)
        assert result['success'] is False
        assert "处理器名称不能为空" in result['error']
    
    def test_add_alarm_handler_invalid_func(self, monitor_controller):
        result = monitor_controller.add_alarm_handler("test_handler", "not_callable")
        assert result['success'] is False
        assert "处理器必须是可调用对象" in result['error']
    
    def test_add_alarm_handler_exception(self, monitor_controller, mock_monitor_service):
        def test_handler(alarm):
            pass
        mock_monitor_service.add_alarm_handler.side_effect = Exception("添加错误")
        result = monitor_controller.add_alarm_handler("test_handler", test_handler)
        assert result['success'] is False
        assert "添加错误" in result['error']
    
    def test_validate_file_path_invalid_extension(self, monitor_controller):
        with patch('pathlib.Path') as mock_path:
            mock_path.return_value.exists.return_value = True
            mock_path.return_value.suffix = '.txt'
            result = monitor_controller._validate_file_path("data/test.txt")
            assert result is False
    
    def test_validate_file_path_nonexistent(self, monitor_controller):
        with patch('pathlib.Path') as mock_path:
            mock_path.return_value.exists.return_value = False
            result = monitor_controller._validate_file_path("nonexistent.dat")
            assert result is False
    
    def test_format_alarm(self, monitor_controller, sample_alarm):
        formatted = monitor_controller._format_alarm(sample_alarm)
        assert formatted['id'] == "ALARM_TEST_001"
        assert formatted['rule_id'] == "test_rule"
        assert formatted['rule_name'] == "测试规则"
        assert formatted['severity'] == "high"
        assert formatted['timestamp'] == sample_alarm.timestamp.isoformat()
        assert formatted['description'] == "测试告警"
        assert formatted['sensor_values'] == {"温度": 25.5} 