# 医疗多模态模型评估流程 

## 概述

本文档详细介绍了医疗多模态模型评估的完整流程，包括数据预处理、模型评估、结果分析和对比分析等步骤。该评估系统支持四种主要任务类型：分类(Classification)、测量(Measurement)、分割(Segmentation)、报告生成(Report Generation)。

## 目录
1. [环境准备](#环境准备)
2. [数据预处理](#数据预处理)
3. [模型评估](#模型评估)
4. [结果表格生成](#结果表格生成)
5. [详细分析工具](#详细分析工具)
6. [常见问题解决](#常见问题解决)
7. [目录结构说明](#目录结构说明)

---

## 环境准备

### Python环境
推荐使用conda管理Python环境，特别是处理pandas相关任务时：

```bash
conda activate multimodal_test
```

### 依赖包
确保安装以下主要依赖：
- pandas
- numpy
- scikit-learn
- torch (用于BERTScore计算)
- transformers
- pycocoevalcap (用于BLEU和ROUGE评估)
- pillow (用于图像处理)

---

## 数据预处理

### 第一步：模型回复处理

#### 1.1 分类/分割任务回复提取

**程序路径**: `scripts/extract_model_responses_final.py`

**功能**: 从JSONL文件中提取和清理模型回复，特别适用于选择题类型的分类和分割任务。

**使用方法**:
```bash
# 处理单个文件
python3 scripts/extract_model_responses_final.py \
    --input /path/to/input.jsonl \
    --output /path/to/output.jsonl \
    --debug

# 处理整个目录（推荐）
python3 scripts/extract_model_responses_final.py \
    --input /path/to/input_directory \
    --output /path/to/output_directory
```

**主要功能**:
- 从问题文本中自动提取选项列表
- 支持多种选项格式（引号分隔、逗号分隔等）
- 智能匹配模型回复与正确选项
- 处理特殊任务（如BI-RADS分级、解剖结构识别等）
- 保留原始回复并输出清理后的预测值

#### 1.2 测量任务数值提取

**程序路径**: `scripts/extract_measurement_values_improved.py`

**功能**: 从模型回复中提取数值，专用于测量任务。

**使用方法**:
```bash
# 处理单个文件
python3 scripts/extract_measurement_values_improved.py \
    --input /path/to/input.jsonl \
    --output /path/to/output.jsonl \
    --task-id 57

# 处理整个目录（推荐）
python3 scripts/extract_measurement_values_improved.py \
    --input /path/to/input_directory \
    --output /path/to/output_directory
```

**主要功能**:
- 智能数值提取，支持多种数值格式
- 针对不同任务ID使用特定的提取策略
- 任务57（肝脏脂肪）：匹配百分比和脂肪含量描述
- 任务50（IMT测量）：匹配毫米单位和IMT相关描述
- 详细的日志记录和统计信息

**重要提示**: 
- 处理单个文件时必须提供`--task-id`参数
- 处理目录时会自动根据目录结构识别任务ID
- 详细日志保存在`extract_measurement_values_improved.log`

---

## 模型评估

### 第二步：创建结果目录结构

在开始评估前，需要为每个任务创建标准的results文件夹结构：

```bash
mkdir -p /path/to/your_model_results/{task_id}/{model_name}/
```

例如：
```bash
mkdir -p /path/to/DolphinV1.9_results/03/DolphinV1.9/
mkdir -p /path/to/DolphinV1.9_results/21/DolphinV1.9/
# ... 为每个任务和模型创建目录
```

### 第三步：运行评估程序

**评估程序路径**: `new_results/`

#### 3.1 分类任务评估

**程序**: `qwen_cla_eval.py`

**支持的数据集**:
- 超声平面识别 (03, 10, 18, 69, anatomy)
- 乳腺超声分类 (21, 25, 40, 42)
- 胎儿相关 (23, 32, 44, 57, 66, 70, 75)
- 其他专业分类任务

**使用方法**:
```bash
cd new_results
python3 qwen_cla_eval.py /path/to/model_results /path/to/output_results.txt
```

**评估指标**:
- Accuracy (准确率)
- Precision (精确率)  
- Recall (召回率)
- F1-Score (F1分数)

#### 3.2 测量任务评估

**程序**: `qwen_measure_eval.py`

**支持的数据集**:
- 心脏测量 (18)
- IMT测量 (27, 50)  
- 肝脏脂肪含量 (57)

**使用方法**:
```bash
cd new_results
python3 qwen_measure_eval.py /path/to/model_results /path/to/output_results.txt
```

**评估指标**:
- RMSE (均方根误差)
- MAE (平均绝对误差)
- %_within_tolerance (容差范围内百分比)
- Std (标准差)

#### 3.3 分割任务评估

**程序**: `qwen_seg_eval.py`

**支持的数据集**:
- 病灶定位 (04, 17, 23, 32, 64)
- 目标检测 (09, 13, 16, 18, 31, 37, 38, 47, 49, 50, 52, 53, 67)
- 关键点检测 (48)

**使用方法**:
```bash
cd new_results
python3 qwen_seg_eval.py /path/to/model_results /path/to/output_results.txt
```

**评估指标**:
- Accuracy (准确率)

#### 3.4 报告生成任务评估

**程序**: `qwen_report_eval.py`

**支持的数据集**:
- 报告生成 (39)
- 标题生成 (10, 44)

**使用方法**:
```bash
cd new_results
python3 qwen_report_eval.py /path/to/model_results /path/to/output_results.txt
```

**评估指标**:
- BLEU-1/2/3/4 (双语评估)
- ROUGE (摘要质量)
- BERTScore (语义相似度)

**注意事项**:
- 报告生成评估需要加载BERT模型，首次运行较慢
- 如果有本地BERT模型，可修改程序中的`HAVE_LOCAL_BERTSCORE_MODEL`配置

---

## 结果表格生成

### 第四步：生成评估结果表格

**程序路径**: `table_fill/update_table_score_format.py`

**功能**: 读取各任务的评估结果文件，计算综合得分，生成LaTeX格式的结果表格。

**使用方法**:
```bash
cd table_fill
python3 update_table_score_format.py
```

**输入文件** (程序自动读取):
- `/path/to/DolphinV1.9p_results/cla_results.txt`
- `/path/to/DolphinV1.9p_results/seg_results.txt`
- `/path/to/DolphinV1.9p_results/mea_results.txt`
- `/path/to/DolphinV1.9p_results/report_results.txt`

**输出文件**:
- `table_fill/new_table_content_score_format0522.tex`

**功能特点**:
- 自动计算各任务加权得分
- 按模型类型分组（医疗专用、开源、闭源）
- 生成标准的LaTeX表格格式
- 包含随机猜测基线对比

**任务权重配置**:
```python
weights = {
    'diag': 0.2,    # 诊断任务
    'vra': 0.2,     # 视图识别
    'll': 0.07,     # 病灶定位
    'od': 0.27,     # 目标检测
    'kd': 0.07,     # 关键点检测
    'cve': 0.07,    # 连续值估计
    'rg': 0.08,     # 报告生成
    'cg': 0.04      # 标题生成
}
```

---

## 详细分析工具

### 第五步：使用模型对比分析工具包（可选）

**工具包路径**: `Model_Comparison_Toolkit/`

这是一个功能强大的分析工具包，支持详细的模型对比、可视化和案例分析。

#### 5.1 主要对比工具

**程序**: `model_comparison_toolkit.py`

**功能**: 
- 全面的模型性能对比
- 多指标可视化图表生成
- 支持标准模式和深度推理模式对比
- 生成详细的分析报告

**使用方法**:
```bash
cd Model_Comparison_Toolkit

# 基本对比分析
python3 model_comparison_toolkit.py \
    --model1-name "Dolphin-1.6" \
    --model1-data /path/to/model1/results \
    --model2-name "Dolphin-1.9" \
    --model2-data /path/to/model2/results \
    --output-dir /path/to/output

# 使用预设的Dolphin对比
bash example_dolphin_comparison.sh
```

**输出内容**:
- 详细的性能对比报告 (Markdown格式)
- 各任务各指标的PNG图表
- 数据文件和脚本的完整副本
- 可直接用于论文的表格和图表

#### 5.2 专门的分析工具

**Dolphin版本深入分析**:
```bash
cd Model_Comparison_Toolkit/Dolphin_Fixed_Analysis
bash generate_case_report.sh
```

**功能**:
- 生成三案例对比报告
- 提取具体的错误案例和成功案例
- 包含图像预览和详细分析
- 自动嵌入base64编码的图像

#### 5.3 可视化功能

**支持的图表类型**:
1. **任务性能对比图**: 展示不同模型在各任务上的表现
2. **指标热力图**: 直观显示多维度性能差异
3. **趋势分析图**: 显示模型版本演进的性能变化
4. **错误案例分析**: 具体案例的详细对比

**图表特点**:
- 高质量PNG输出，适合论文发表
- 英文标题和标签
- 统一的配色方案和样式
- 支持子图和多指标并列显示

---

## 常见问题解决

### 6.1 环境相关问题

**问题**: `ValueError: numpy.dtype size changed`
**解决方案**: 
```bash
conda activate multimodal_test
pip install --upgrade pandas numpy
```

**问题**: `No module named 'pycocoevalcap'`
**解决方案**:
```bash
pip install pycocoevalcap
# 或者从源码安装
git clone https://github.com/salaniz/pycocoevalcap
cd pycocoevalcap && pip install .
```

### 6.2 数据处理问题

**问题**: TSV文件读取错误 `field larger than field limit`
**解决方案**: 程序已内置处理，如仍有问题可增加字段大小限制：
```python
import csv
csv.field_size_limit(1000000)
```

**问题**: 图像路径提取失败
**解决方案**: 检查JSONL文件中的images字段格式，确保是数组格式 `["path/to/image.jpg"]`

### 6.3 评估相关问题

**问题**: 某些任务评分为0
**解决方案**: 
1. 检查数据预处理是否正确完成
2. 确认TSV文件路径正确
3. 验证模型输出格式是否符合要求

**问题**: BERTScore计算过慢
**解决方案**: 
1. 使用GPU加速: `export CUDA_VISIBLE_DEVICES=0`
2. 下载本地BERT模型，修改程序配置

---

## 目录结构说明

### 7.1 标准的模型结果目录结构

```
model_results/
├── task_id_1/
│   ├── model_name_1/
│   │   └── results.jsonl
│   ├── model_name_2/
│   │   └── results.jsonl
│   └── ...
├── task_id_2/
│   ├── model_name_1/
│   │   └── results.jsonl
│   └── ...
└── ...
```

### 7.2 评估输出目录结构

```
evaluation_results/
├── cla_results.txt      # 分类任务结果
├── seg_results.txt      # 分割任务结果
├── mea_results.txt      # 测量任务结果
├── report_results.txt   # 报告生成结果
└── summary_report.md    # 综合分析报告
```

### 7.3 DolphinV1.9三案例对比报告生成

**工具位置**: `Model_Comparison_Toolkit/Dolphin_Fixed_Analysis/`

这个工具专门为DolphinV1.9模型的标准模式与深度推理模式对比而设计。

**使用方法**:
```bash
cd Model_Comparison_Toolkit/Dolphin_Fixed_Analysis
bash generate_case_report.sh
```

**输出文件**:
- `DolphinV1.9_三案例对比报告.md` - 包含三个具体案例的详细对比
- 自动嵌入base64编码的图像，可直接查看

**报告内容**:
1. **案例1**: 超声图像位置识别 (任务48)
2. **案例2**: 甲状腺结节分割 (任务31) 
3. **案例3**: 胎儿超声平面分类 (任务03)

每个案例包括：
- 原始图像（base64嵌入）
- 参考答案
- 标准模式回复
- 深度推理模式回复
- 准确性分析
- 回复长度对比

---

## 快速开始示例

以下是一个完整的评估流程示例：

```bash
# 1. 激活环境
conda activate multimodal_test

# 2. 数据预处理
python3 scripts/extract_model_responses_final.py \
    --input /path/to/raw_model_outputs \
    --output /path/to/processed_outputs

python3 scripts/extract_measurement_values_improved.py \
    --input /path/to/measurement_outputs \
    --output /path/to/processed_measurement_outputs

# 3. 创建结果目录
mkdir -p ./MyModel_results

# 4. 运行评估
cd new_results
python3 qwen_cla_eval.py /path/to/processed_outputs ./../MyModel_results/cla_results.txt
python3 qwen_seg_eval.py /path/to/processed_outputs ./../MyModel_results/seg_results.txt
python3 qwen_measure_eval.py /path/to/processed_measurement_outputs ./../MyModel_results/mea_results.txt
python3 qwen_report_eval.py /path/to/processed_outputs ./../MyModel_results/report_results.txt

# 5. 生成表格（需要修改程序中的路径配置）
cd ../table_fill
python3 update_table_score_format.py

# 6. 对比分析（可选）
cd ../Model_Comparison_Toolkit
python3 model_comparison_toolkit.py \
    --model1-name "BaselineModel" \
    --model1-data /path/to/baseline/results \
    --model2-name "MyModel" \
    --model2-data ./../MyModel_results \
    --output-dir ./../MyModel_Analysis
```

---

## 核心程序详细说明

### 1. 数据预处理程序

#### extract_model_responses_final.py
- **位置**: `scripts/extract_model_responses_final.py`
- **用途**: 处理分类和分割任务的模型回复
- **特色功能**:
  - 自动选项提取和匹配
  - 支持多种选项格式识别
  - 特殊任务定制处理（BI-RADS、解剖结构等）
  - 详细的处理统计和日志

#### extract_measurement_values_improved.py  
- **位置**: `scripts/extract_measurement_values_improved.py`
- **用途**: 提取测量任务中的数值
- **特色功能**:
  - 智能数值识别和提取
  - 任务特定的提取策略
  - 支持百分比、毫米等多种单位
  - 完整的统计分析报告

### 2. 评估程序系列

#### qwen_cla_eval.py
- **位置**: `new_results/qwen_cla_eval.py`
- **支持任务**: 分类任务 (03, 10, 18, 21, 23, 25, 28_1, 32, 37, 40, 42, 44, 50, 53, 57, 66, 69, 70, 74is_normal, 74is_visible, 75, anatomy)
- **输出指标**: Accuracy, Precision, Recall, F1-Score

#### qwen_measure_eval.py
- **位置**: `new_results/qwen_measure_eval.py`  
- **支持任务**: 测量任务 (18, 27, 31, 50, 57)
- **输出指标**: RMSE, MAE, %_within_tolerance, Std

#### qwen_seg_eval.py
- **位置**: `new_results/qwen_seg_eval.py`
- **支持任务**: 分割任务 (04, 09, 13, 16, 17, 18, 23, 31, 32, 37, 38, 47, 48, 49, 50, 52, 53, 64, 67)
- **输出指标**: Accuracy

#### qwen_report_eval.py
- **位置**: `new_results/qwen_report_eval.py`
- **支持任务**: 报告生成 (10, 39, 44)
- **输出指标**: BLEU-1/2/3/4, ROUGE, BERTScore

### 3. 结果处理程序

#### update_table_score_format.py
- **位置**: `table_fill/update_table_score_format.py`
- **功能**: 
  - 读取四个评估结果文件
  - 按任务类型分组统计
  - 计算加权综合得分
  - 生成LaTeX格式表格
- **输出**: LaTeX表格代码文件

### 4. 分析工具包

#### Model_Comparison_Toolkit
- **位置**: `Model_Comparison_Toolkit/`
- **核心程序**: `model_comparison_toolkit.py`
- **专用工具**: `Dolphin_Fixed_Analysis/`子目录
- **功能**:
  - 多模型性能对比
  - 可视化图表生成
  - 案例提取和分析
  - 详细报告生成

---

## 重要提醒和最佳实践

### 数据一致性
1. 确保所有评估使用相同的预处理后数据
2. 验证TSV文件路径正确且可访问
3. 检查模型输出格式的一致性

### 性能优化
1. 使用`multimodal_test`环境避免依赖冲突
2. 对于大规模评估，考虑分批处理
3. BERTScore计算较慢，可考虑使用GPU或本地模型

### 结果验证
1. 对比随机猜测基线确认结果合理性
2. 查看详细日志文件排查异常
3. 使用小样本验证流程正确性

---

*文档版本: 2024-01-11*  
*最后更新: 工作交接时*
*维护者: [工作交接]*

