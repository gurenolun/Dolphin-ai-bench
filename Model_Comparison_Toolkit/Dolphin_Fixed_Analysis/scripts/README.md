# Dolphin模型三案例对比报告生成器

## 概述

`generate_three_case_comparison.py` 是一个用于生成DolphinV1.6模型三案例对比报告的程序。该程序基于原始的 `extract_all_seg_examples_english.py` 的逻辑开发，专门用于对比Dolphin标准模式和深度推理模式在特定案例上的表现。

## 功能特点

- **三个预定义案例**：分别来自不同任务类型（分割任务48、分割任务31、分类任务03）
- **双模式对比**：同时展示标准模式(DolphinV1.6r)和深度推理模式(DolphinV1.6rd)的回答
- **图像嵌入**：自动将图像转换为base64格式嵌入到报告中
- **参考答案**：提供每个案例的标准答案
- **格式化输出**：生成结构化的Markdown报告

## 程序结构

### 主要函数

1. **`extract_coordinates()`** - 从字符串中提取坐标信息
2. **`get_bounding_box_location()`** - 确定边界框的位置类别
3. **`try_load_image()`** - 加载图像并转换为base64格式
4. **`read_tsv_data()`** - 读取TSV标注文件
5. **`find_model_jsonl_file()`** - 查找模型输出的JSONL文件
6. **`read_model_response()`** - 读取模型响应
7. **`generate_three_case_comparison()`** - 生成完整的对比报告

### 预定义案例

```python
cases = [
    {
        'task_id': '48',
        'index': 47,  # 任务48的第48个样本
        'title': '案例 1: seg (任务48)'
    },
    {
        'task_id': '31', 
        'index': 30,  # 任务31的第31个样本
        'title': '案例 2: seg (任务31)'
    },
    {
        'task_id': '03',
        'index': 2,   # 任务03的第3个样本
        'title': '案例 3: 分类任务 (任务03)'
    }
]
```

## 使用方法

### 基本运行

```bash
cd Model_Comparison_Toolkit/Dolphin_Fixed_Analysis/scripts/
python generate_three_case_comparison.py
```

### 输出文件

程序会生成两个相同的报告文件：
1. `DolphinV1.6_三案例对比报告.md` - 在scripts目录下
2. `../reports/DolphinV1.6_三案例对比报告.md` - 在reports目录下

## 配置说明

### TSV路径配置

```python
TSV_PATH = {
    '03': '/media/ps/data-ssd/json_processing/ale_tsv_output/03.tsv',
    '31': '/media/ps/data-ssd/json_processing/ale_tsv_output/31.tsv',
    '48': '/media/ps/data-ssd/json_processing/ale_tsv_output/single_keypoint/48.tsv'
}
```

### 模型输出目录

```python
MODEL_OUTPUT_DIR = '/media/ps/data-ssd/benchmark/VLMEvalKit/outputs/dolphin-output'
```

### 目标模型配置

```python
target_models = {
    'standard': 'DolphinV1.6r',        # 标准模式
    'deep_reasoning': 'DolphinV1.6rd'  # 深度推理模式
}
```

## 报告格式

生成的报告包含以下部分：

### 每个案例的结构
- **标题** - 案例编号和任务描述
- **图像** - base64编码的图像数据
- **标准模型回答** - DolphinV1.6r的响应
- **深度推理模型回答** - DolphinV1.6rd的响应（自动提取</think>后的内容）
- **参考答案** - 标准答案或坐标信息

### 示例输出格式

```markdown
# DolphinV1.6模型三案例对比

## 案例 1: seg (任务48)

**图像**:
![案例1图像](data:image/jpeg;base64,...)

**标准模型回答**:
```
upper center
```

**深度推理模型回答**:
```
The keypoint is evident in the upper center.
```

**参考答案**:
```
upper center
```
```

## 依赖要求

- pandas
- numpy
- PIL (Pillow)
- matplotlib
- base64 (内置)
- json (内置)
- glob (内置)

## 注意事项

1. **路径配置**：确保TSV文件路径和模型输出目录路径正确
2. **文件权限**：确保程序有读取TSV文件和模型输出文件的权限
3. **图像处理**：大图像会被转换为base64，可能导致报告文件较大
4. **深度推理模式**：程序会自动提取`</think>`标签后的内容作为最终回答

## 错误处理

程序包含完善的错误处理机制：
- TSV文件读取失败时会显示错误信息
- 模型文件不存在时会跳过该模型
- 图像加载失败时会显示占位符
- 索引超出范围时会显示警告信息

## 扩展性

可以通过修改以下部分来扩展程序：
- 修改`cases`列表来改变对比的案例
- 修改`target_models`来对比不同的模型
- 调整`TSV_PATH`来支持更多任务
- 自定义输出格式和报告结构 