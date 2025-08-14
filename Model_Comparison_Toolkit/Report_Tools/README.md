# Report Tools (Anonymized)

本目录提供匿名化的报告生成工具，默认使用相对目录，不包含任何本地绝对路径或特定任务编号。可直接在仓库中运行。

目录：

- `generate_three_case_comparison.py`: 生成三案例对比报告（标准模式 vs 深度推理模式）。

默认目录结构（可自定义）：

```
data/
  models/
    Standard/<task_type>/<task_id>/**.jsonl
    Deep/<task_type>/<task_id>/**.jsonl
  tsv/
    <task_type>/<task_id>.tsv  或  <task_id>.tsv
```

用法示例：

```bash
cd Model_Comparison_Toolkit/Report_Tools
python3 generate_three_case_comparison.py \
  --standard-dir data/models/Standard \
  --deep-dir data/models/Deep \
  --tsv-root data/tsv \
  --output Three_Case_Comparison_Report.md \
  --task cla:task_A:0:Task A \
  --task seg:task_B:0:Task B \
  --task report:task_C:0:Task C
```

说明：
- `--task` 可重复传参，格式为 `type:id:index:desc`；若不提供，将使用匿名化的默认三案例。
- 支持任务类型：`cla`（分类）、`seg`（分割/定位）、`report`（报告/标题）。
- 工具会尝试嵌入图片（如果可找到路径），否则显示占位提示。

