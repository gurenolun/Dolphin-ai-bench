# Model Comparison Toolkit

一个通用的模型性能对比分析工具包，支持命令行操作，可扩展用于测试任何模型。

## 🎯 主要特性

- **命令行界面**: 灵活的参数配置
- **通用性**: 支持任意两个模型的对比
- **可扩展性**: 易于适配新的模型和数据格式
- **完整分析**: 图表、报告、数据一体化输出
- **修复优化**: 解决了标题过长和指标选择问题

## 🚀 快速开始

### 基本用法

```bash
python3 model_comparison_toolkit.py \
    --model1-name "Dolphin-1.6" \
    --model2-name "Dolphin-1.9" \
    --model1-standard-dir /path/to/dolphin16/standard \
    --model2-standard-dir /path/to/dolphin19/standard
```

### 完整用法（包含深度推理模式）

```bash
python3 model_comparison_toolkit.py \
    --model1-name "Dolphin-1.6" \
    --model2-name "Dolphin-1.9" \
    --model1-standard-dir /path/to/dolphin16/standard \
    --model2-standard-dir /path/to/dolphin19/standard \
    --model1-deep-dir /path/to/dolphin16/deep \
    --model2-deep-dir /path/to/dolphin19/deep \
    --include-deep \
    --output-dir "Custom_Analysis_Output"
```

## 📋 参数说明

| 参数 | 必需 | 说明 |
|------|------|------|
| `--model1-name` | ✅ | 第一个模型的名称 |
| `--model2-name` | ✅ | 第二个模型的名称 |
| `--model1-standard-dir` | ✅ | 模型1标准模式结果目录 |
| `--model2-standard-dir` | ✅ | 模型2标准模式结果目录 |
| `--model1-deep-dir` | ❌ | 模型1深度推理模式结果目录 |
| `--model2-deep-dir` | ❌ | 模型2深度推理模式结果目录 |
| `--include-deep` | ❌ | 包含深度推理模式对比 |
| `--output-dir` | ❌ | 自定义输出目录（默认自动生成） |

## 📊 支持的任务类型

### 分类任务 (Classification)
- **指标**: 准确率、精确率、召回率、F1分数
- **文件**: `cla_results.txt`

### 测量任务 (Measurement)  
- **指标**: RMSE、MAE、容差内百分比
- **文件**: `mea_results.txt`
- **修复**: 移除了failed_items指标

### 分割任务 (Segmentation)
- **指标**: 准确率
- **文件**: `seg_results.txt`
- **修复**: 优化了标题显示

### 报告生成任务 (Report Generation)
- **指标**: BLEU-1/2/3/4、Rouge、BERTScore
- **文件**: `report_results.txt`
- **修复**: 优化了标题显示，防止超出

## 📁 数据格式要求

每个结果目录需要包含以下文件：
```
results_directory/
├── cla_results.txt      # 分类任务结果
├── mea_results.txt      # 测量任务结果
├── seg_results.txt      # 分割任务结果
└── report_results.txt   # 报告生成任务结果
```

每个文件应为TSV格式，包含 `task_id` 列和相应的指标列。

## 🎨 输出内容

### 生成的文件结构
```
ModelA_vs_ModelB_Analysis_20250711_HHMMSS/
├── charts/              # PNG图表文件
├── reports/             # 详细分析报告
├── data/               # 原始数据副本
├── scripts/            # 图表生成脚本
├── README.md           # 分析说明
└── generate_all_charts.sh  # 批量生成脚本
```

### 图表特性
- **高分辨率PNG**: 适合报告和演示
- **子图布局**: 每个任务的所有指标在一个图表中
- **完整标签**: 横坐标显示所有数据集ID
- **优化标题**: 自动处理过长标题
- **专业配色**: 模型1(蓝色) vs 模型2(紫红色)

## 🔧 使用示例

### 示例1: 对比两个Dolphin版本
```bash
python3 model_comparison_toolkit.py \
    --model1-name "Dolphin-1.6" \
    --model2-name "Dolphin-1.9" \
    --model1-standard-dir "/home/user/DolphinV1.6r_results" \
    --model2-standard-dir "/home/user/DolphinV1.9p_results" \
    --model1-deep-dir "/home/user/DolphinV1.6rd_results" \
    --model2-deep-dir "/home/user/DolphinV1.9_results" \
    --include-deep
```

### 示例2: 对比不同模型系列
```bash
python3 model_comparison_toolkit.py \
    --model1-name "GPT-4" \
    --model2-name "Claude-3" \
    --model1-standard-dir "/data/gpt4_results" \
    --model2-standard-dir "/data/claude3_results" \
    --output-dir "GPT4_vs_Claude3_Analysis"
```

### 示例3: 只对比标准模式
```bash
python3 model_comparison_toolkit.py \
    --model1-name "Model-A" \
    --model2-name "Model-B" \
    --model1-standard-dir "/results/modelA" \
    --model2-standard-dir "/results/modelB"
```

## 🛠️ 技术要求

### 依赖项
- Python 3.6+
- PIL (Pillow) - 用于PNG图表生成

### 安装依赖
```bash
pip install Pillow
```

### 系统要求
- Linux/macOS/Windows
- 支持中文字体的系统（可选）

## 🎯 核心改进

### 相比之前版本的改进
1. **移除failed_items**: 测量任务不再包含failed_items指标
2. **标题优化**: 自动处理过长标题，防止超出图表边界
3. **命令行接口**: 完全可配置的命令行参数
4. **通用性**: 支持任意模型名称和路径
5. **可扩展性**: 易于添加新的任务类型和指标

### 技术优化
- 自动标题换行和截断
- 更好的字体大小控制
- 改进的图表布局算法
- 错误处理和数据验证

## 📈 输出示例

运行成功后会看到类似输出：
```
=== Model Performance Comparison Toolkit ===
Comparing Dolphin-1.6 vs Dolphin-1.9
Output directory: Dolphin-1.6_vs_Dolphin-1.9_Analysis_20250711_172105

1. Loading data...
Loaded /path/to/cla_results.txt: 23 records
...

2. Generating comprehensive task charts with subplots...
Generated analysis report: .../classification_standard_mode_analysis_report.md
...

3. Copying original data files...
Copied /path/to/source -> /path/to/target
...

Model comparison analysis setup completed!
```

## 🤝 扩展指南

### 添加新任务类型
1. 在 `task_metrics` 字典中添加新任务
2. 定义相应的指标列表
3. 确保数据文件命名遵循 `{task}_results.txt` 格式

### 添加新指标
1. 在相应任务的指标列表中添加 `(column_name, display_name)` 元组
2. 确保数据文件中包含相应列

### 自定义图表样式
1. 修改 `generate_task_subplot_png_script` 函数中的颜色定义
2. 调整字体大小和图表尺寸参数

---

**版本**: 1.0  
**更新时间**: 2025-01-11  
**兼容性**: Python 3.6+ 