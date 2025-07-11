"""
tests/unit/test_data_controller.py
------------------------------------
数据控制器单元测试
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from pathlib import Path

from backend.app.controllers.DataController import DataController
from backend.app.entities.Record import Record


class TestDataController:
    """数据控制器测试类"""
    
    @pytest.fixture
    def data_controller(self):
        return DataController()
    
    @pytest.fixture
    def sample_records(self):
        return [
            Record(
                run_id="test_run",
                ts=datetime(2024, 1, 1, 12, 0, 0),
                metrics={"温度": 25.5, "湿度": 60.0},
                file_pos=1000
            ),
            Record(
                run_id="test_run",
                ts=datetime(2024, 1, 1, 12, 1, 0),
                metrics={"温度": 26.0, "湿度": 61.0},
                file_pos=2000
            ),
            Record(
                run_id="test_run",
                ts=datetime(2024, 1, 1, 12, 2, 0),
                metrics={"温度": 24.5, "湿度": 59.0},
                file_pos=3000
            )
        ]
    
    @patch('backend.app.controllers.DataController.iter_new_records')
    def test_parse_data_file_success(self, mock_iter_records, data_controller, sample_records):
        mock_iter_records.return_value = sample_records
        with patch.object(data_controller, '_validate_file_path', return_value=True):
            result = data_controller.parse_data_file("data/test.dat", "test_run")
        
        assert result['success'] is True
        assert result['data']['file_path'] == "data/test.dat"
        assert result['data']['run_id'] == "test_run"
        assert result['data']['total_records'] == 3
        assert len(result['data']['records']) == 3
        
        first_record = result['data']['records'][0]
        assert first_record['run_id'] == "test_run"
        assert first_record['metrics'] == {"温度": 25.5, "湿度": 60.0}
        assert first_record['file_pos'] == 1000
    
    @patch('backend.app.controllers.DataController.iter_new_records')
    def test_parse_data_file_with_range(self, mock_iter_records, data_controller, sample_records):
        mock_iter_records.return_value = sample_records
        with patch.object(data_controller, '_validate_file_path', return_value=True):
            result = data_controller.parse_data_file("data/test.dat", "test_run", start_record=1, end_record=2)
        
        assert result['success'] is True
        assert result['data']['total_records'] == 1
        assert len(result['data']['records']) == 1
    
    def test_parse_data_file_invalid_path(self, data_controller):
        result = data_controller.parse_data_file("nonexistent.dat", "test_run")
        
        assert result['success'] is False
        assert "文件不存在或格式错误" in result['error']
    
    @patch('backend.app.controllers.DataController.iter_new_records')
    def test_parse_data_file_exception(self, mock_iter_records, data_controller):
        mock_iter_records.side_effect = Exception("解析错误")
        with patch.object(data_controller, '_validate_file_path', return_value=True):
            result = data_controller.parse_data_file("data/test.dat", "test_run")
        
        assert result['success'] is False
        assert "解析错误" in result['error']
    
    def test_get_file_info_nonexistent(self, data_controller):
        with patch('pathlib.Path') as mock_path_class:
            mock_path = Mock()
            mock_path.exists.return_value = False
            mock_path_class.return_value = mock_path
            
            result = data_controller.get_file_info("nonexistent.dat")
            
            assert result['success'] is False
            assert "文件不存在" in result['error']
    
    @patch('backend.app.controllers.DataController.iter_new_records')
    def test_get_data_statistics_success(self, mock_iter_records, data_controller, sample_records):
        mock_iter_records.return_value = sample_records
        with patch.object(data_controller, '_validate_file_path', return_value=True):
            result = data_controller.get_data_statistics("data/test.dat", "test_run")
        
        assert result['success'] is True
        assert result['data']['total_records'] == 3
        
        time_range = result['data']['time_range']
        assert time_range['start'] == sample_records[0].ts.isoformat()
        assert time_range['end'] == sample_records[-1].ts.isoformat()
        assert time_range['duration_minutes'] == 2.0
        
        sensors = result['data']['sensors']
        assert '温度' in sensors
        assert '湿度' in sensors
        assert sensors['温度']['count'] == 3
        assert sensors['温度']['min'] == 24.5
        assert sensors['温度']['max'] == 26.0
        assert pytest.approx(sensors['温度']['avg']) == 25.333333333333332
    
    @patch('backend.app.controllers.DataController.iter_new_records')
    def test_get_data_statistics_empty_data(self, mock_iter_records, data_controller):
        mock_iter_records.return_value = []
        with patch.object(data_controller, '_validate_file_path', return_value=True):
            result = data_controller.get_data_statistics("data/test.dat", "test_run")
        
        assert result['success'] is True
        assert result['data']['total_records'] == 0
        assert result['data']['time_range'] is None
        assert result['data']['sensors'] == {}
        assert result['data']['statistics'] == {}
    
    @patch('backend.app.controllers.DataController.iter_new_records')
    def test_get_data_statistics_exception(self, mock_iter_records, data_controller):
        mock_iter_records.side_effect = Exception("统计错误")
        with patch.object(data_controller, '_validate_file_path', return_value=True):
            result = data_controller.get_data_statistics("data/test.dat", "test_run")
        
        assert result['success'] is False
        assert "统计错误" in result['error']
    
    def test_validate_file_path_invalid_extension(self, data_controller):
        with patch('pathlib.Path') as mock_path_class:
            mock_path = Mock()
            mock_path.exists.return_value = True
            mock_path.suffix = '.txt'
            mock_path_class.return_value = mock_path
            
            result = data_controller._validate_file_path("data/test.txt")
            assert result is False
    
    def test_validate_file_path_nonexistent(self, data_controller):
        with patch('pathlib.Path') as mock_path_class:
            mock_path = Mock()
            mock_path.exists.return_value = False
            mock_path_class.return_value = mock_path
            
            result = data_controller._validate_file_path("nonexistent.dat")
            assert result is False
    
    def test_format_record(self, data_controller):
        record = Record(
            run_id="test_run",
            ts=datetime(2024, 1, 1, 12, 0, 0),
            metrics={"温度": 25.5, "湿度": 60.0},
            file_pos=1000
        )
        
        formatted = data_controller._format_record(record)
        
        assert formatted['run_id'] == "test_run"
        assert formatted['timestamp'] == record.ts.isoformat()
        assert formatted['metrics'] == {"温度": 25.5, "湿度": 60.0}
        assert formatted['file_pos'] == 1000
    
    def test_analyze_sensors(self, data_controller, sample_records):
        sensors = data_controller._analyze_sensors(sample_records)
        
        assert '温度' in sensors
        assert '湿度' in sensors
        
        temp_stats = sensors['温度']
        assert temp_stats['count'] == 3
        assert temp_stats['min'] == 24.5
        assert temp_stats['max'] == 26.0
        assert pytest.approx(temp_stats['avg']) == 25.333333333333332
        
        humidity_stats = sensors['湿度']
        assert humidity_stats['count'] == 3
        assert humidity_stats['min'] == 59.0
        assert humidity_stats['max'] == 61.0
        assert humidity_stats['avg'] == 60.0
    
    def test_analyze_sensors_empty(self, data_controller):
        sensors = data_controller._analyze_sensors([])
        assert sensors == {} 