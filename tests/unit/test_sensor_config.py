# tests/unit/test_sensor_config.py
import pytest
from datetime import datetime

from backend.app.entities.sensor_config import (
    SensorChannel, SensorType, Unit, TestSession, SensorGroup
)


# ---------- 测试用例 -------------------------------------------------

def test_sensor_channel_creation():
    """测试传感器通道创建"""
    sensor = SensorChannel(
        label="TCEC",
        channel="T1",
        sensor_type=SensorType.TEMPERATURE,
        unit=Unit.CELSIUS,
        description="蒸发器温度传感器"
    )
    
    assert sensor.label == "TCEC"
    assert sensor.channel == "T1"
    assert sensor.sensor_type == SensorType.TEMPERATURE
    assert sensor.unit == Unit.CELSIUS
    assert sensor.enabled is True


def test_test_session_creation():
    """测试测试会话创建"""
    session = TestSession(
        session_id="TEST_2025_001",
        name="冰箱制冷性能测试",
        engineer="张工程师",
        test_type="制冷性能"
    )
    
    assert session.session_id == "TEST_2025_001"
    assert session.name == "冰箱制冷性能测试"
    assert session.engineer == "张工程师"
    assert session.test_type == "制冷性能"


def test_test_session_with_sensors():
    """测试包含传感器的测试会话"""
    sensor = SensorChannel(
        label="TCEC",
        channel="T1",
        sensor_type=SensorType.TEMPERATURE,
        unit=Unit.CELSIUS
    )
    
    session = TestSession(
        session_id="TEST_2025_001",
        name="测试",
        sensors={"TCEC": sensor}
    )
    
    assert "TCEC" in session.sensors
    assert session.sensors["TCEC"].label == "TCEC"


def test_sensor_group():
    """测试传感器分组"""
    group = SensorGroup(
        name="温度传感器",
        description="所有温度相关传感器",
        sensors=["TCEC", "TA1", "TRC1"],
        color="#FF0000"
    )
    
    assert group.name == "温度传感器"
    assert len(group.sensors) == 3
    assert "TCEC" in group.sensors
    assert group.color == "#FF0000"
    assert group.enabled is True


def test_enum_values():
    """测试枚举值"""
    assert SensorType.TEMPERATURE.value == "temperature"
    assert Unit.CELSIUS.value == "°C"


def test_sensor_config_minimal():
    """测试最小化的传感器配置"""
    # 测试只有必需字段的配置
    sensor = SensorChannel(
        label="DOOR_STATUS",
        channel="DI1",
        sensor_type=SensorType.DIGITAL,
        unit=Unit.BOOLEAN
    )
    
    assert sensor.label == "DOOR_STATUS"
    assert sensor.channel == "DI1"
    assert sensor.description == ""  # 默认值
    assert sensor.enabled is True    # 默认值 