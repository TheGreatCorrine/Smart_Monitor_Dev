# Channel配置指南（精简版）

本系统通过 `config/label_channel_match.yaml` 文件实现对所有监控通道的分层标签配置。请根据实际测试需求维护该文件。

## 1. 配置结构

- **channel_categories**: 顶层分组，包含所有监控大类。
  - 每个大类下有：
    - `category_name`: 中文显示名
    - `category_description`: 简要说明
    - `channels`: 该类下所有物理通道（如 T1、TE1、DE1 等）
    - `subtypes`: 该类下所有可选标签（label），每个包含：
      - `subtype_id`: 唯一ID（字符串）
      - `label`: 用户界面显示名
      - `tag`: 简短标记
      - `description`: 详细说明
      - `unit`: 单位
      - `typical_range`: 合理范围（如 [0.0, 100.0]）
      - `is_default`: 是否为默认选项

## 2. 填写要点

- 每个大类至少有1个subtype，且`subtype_id`唯一。
- 每个subtype需填写`label`、`tag`、`description`、`unit`、`typical_range`。
- `is_default: true`表示推荐默认选项。
- `channels`为物理通道ID列表，需与实际采集数据一致。

## 3. 示例片段

```yaml
environment_temp:
  category_name: "环境温度"
  category_description: "冰箱内外环境温度监测"
  channels:
    - AT
  subtypes:
    - subtype_id: "1"
      label: "AT"
      tag: "环境温度"
      description: "可选的环境温度"
      unit: "°C"
      typical_range: [15.0, 35.0]
      is_default: true
```

## 4. 注意事项

- 文件必须为合法YAML格式，缩进需严格对齐。
- 不同大类的`subtype_id`可重复，但同一大类内必须唯一。
- `channels`、`subtypes`均为列表。
- 修改后建议用`python -c "import yaml; yaml.safe_load(open('config/label_channel_match.yaml'))"`验证格式。

## 5. 常见大类说明

- **environment_temp**: 环境温度（AT）
- **total_power**: 整体功率（P）
- **temperature_t**: T1~T22主要温度
- **temperature_te**: TE1~TE14数字温度
- **digital_de**: DE1~DE14数字量

如需扩展/调整，直接编辑`label_channel_match.yaml`即可，无需修改代码。 