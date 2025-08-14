# Model Comparison Toolkit (Anonymized)

该工具包用于对比多模型在不同任务下的表现，输出汇总报告与图表（图表与示例数据不随仓库分发）。发布版本已去除个人绝对路径与本地数据，默认使用相对路径与占位目录。

目录结构（核心部分）：

```
Model_Comparison_Toolkit/
  model_comparison_toolkit.py        # 入口（如有）
  example_dolphin_comparison.sh      # 匿名化示例脚本
  Report_Tools/                      # 报告工具（匿名化）
    generate_three_case_comparison.py
    README.md
```

示例用法：

```bash
cd Model_Comparison_Toolkit

# 直接运行脚本（请先调整示例路径）
bash example_dolphin_comparison.sh

# 或手动调用入口（如有）
python3 model_comparison_toolkit.py \
  --model1-name "Model-1" \
  --model2-name "Model-2" \
  --model1-standard-dir data/models/Standard \
  --model2-standard-dir data/models/Standard \
  --model1-deep-dir data/models/Deep \
  --model2-deep-dir data/models/Deep \
  --include-deep \
  --output-dir outputs/Model_1_vs_2
```

报告工具：

- `Report_Tools/generate_three_case_comparison.py`
  - 从标准/深度推理两套结果中抽取三案例，生成 Markdown 报告
  - 默认匿名任务 ID：`task_A/task_B/task_C`，支持 `--task type:id:index:desc` 自定义
  - 支持目录：`data/models/{Standard,Deep}/<task_type>/<task_id>/**.jsonl` 与 `data/tsv/<task_type>/<task_id>.tsv`

注意：
- 本工具包不包含任何真实数据与生成产物；请在本地准备 `data/` 与 `outputs/` 目录。
- 若你的项目入口脚本名不同，请相应调整示例命令。

