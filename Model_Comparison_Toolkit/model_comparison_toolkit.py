#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import json
import argparse
import shutil
from datetime import datetime

def load_results_txt(file_path):
    """从txt文件加载结果数据"""
    results = []
    if not os.path.exists(file_path):
        return results
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                results.append(row)
        print(f"Loaded {file_path}: {len(results)} records")
    except Exception as e:
        print(f"Failed to load {file_path}: {e}")
    
    return results

def create_task_analysis_report(v1_data, v2_data, task_type, metrics, mode_name, model1_name, model2_name):
    """创建任务分析报告"""
    
    if not v1_data or not v2_data:
        return ""
    
    # 创建任务ID映射
    v1_tasks = {row['task_id']: row for row in v1_data}
    v2_tasks = {row['task_id']: row for row in v2_data}
    
    # 找到共同的任务
    common_tasks = sorted(set(v1_tasks.keys()) & set(v2_tasks.keys()))
    
    if not common_tasks:
        return ""
    
    report = f"""
## {task_type.capitalize()} Task Analysis ({mode_name})

### Performance Summary

| Metric | {model1_name} Avg | {model2_name} Avg | Change | Change % |
|--------|------------------|------------------|--------|----------|
"""
    
    # 计算每个指标的平均值
    for metric, metric_name in metrics:
        v1_values = []
        v2_values = []
        
        for task_id in common_tasks:
            try:
                v1_val = float(v1_tasks[task_id].get(metric, 0))
                v2_val = float(v2_tasks[task_id].get(metric, 0))
                v1_values.append(v1_val)
                v2_values.append(v2_val)
            except (ValueError, TypeError):
                continue
        
        if v1_values and v2_values:
            v1_avg = sum(v1_values) / len(v1_values)
            v2_avg = sum(v2_values) / len(v2_values)
            change = v2_avg - v1_avg
            change_pct = (change / v1_avg * 100) if v1_avg > 0 else 0
            
            report += f"| {metric_name} | {v1_avg:.4f} | {v2_avg:.4f} | {change:+.4f} | {change_pct:+.2f}% |\n"
    
    report += f"""
### Task-by-Task Detailed Comparison

| Task ID | Metric | {model1_name} | {model2_name} | Change % |
|---------|--------|-------------|-------------|----------|
"""
    
    # 详细的任务对比
    for task_id in common_tasks:
        for metric, metric_name in metrics:
            try:
                v1_val = float(v1_tasks[task_id].get(metric, 0))
                v2_val = float(v2_tasks[task_id].get(metric, 0))
                change_pct = ((v2_val - v1_val) / v1_val * 100) if v1_val > 0 else 0
                report += f"| {task_id} | {metric_name} | {v1_val:.4f} | {v2_val:.4f} | {change_pct:+.2f}% |\n"
            except (ValueError, TypeError):
                continue
    
    return report

def generate_task_subplot_png_script(data_dict, task_type, metrics, mode_name, output_dir, model1_name, model2_name):
    """为每个任务生成包含所有指标子图的PNG脚本"""
    
    # 根据任务类型获取数据
    if task_type == 'classification':
        v1_data = data_dict['model1']['cla']
        v2_data = data_dict['model2']['cla']
        chart_title = f'Classification Task Performance ({mode_name})'
    elif task_type == 'measurement':
        v1_data = data_dict['model1']['mea']
        v2_data = data_dict['model2']['mea']
        chart_title = f'Measurement Task Performance ({mode_name})'
    elif task_type == 'segmentation':
        v1_data = data_dict['model1']['seg']
        v2_data = data_dict['model2']['seg']
        chart_title = f'Segmentation Task Performance ({mode_name})'
    elif task_type == 'report':
        v1_data = data_dict['model1']['report']
        v2_data = data_dict['model2']['report']
        chart_title = f'Report Generation Performance ({mode_name})'
    else:
        return None
    
    if not v1_data or not v2_data:
        return None
    
    # 创建任务ID映射
    v1_tasks = {row['task_id']: row for row in v1_data}
    v2_tasks = {row['task_id']: row for row in v2_data}
    
    # 找到共同的任务
    common_tasks = sorted(set(v1_tasks.keys()) & set(v2_tasks.keys()))
    
    if not common_tasks:
        return None
    
    # 为每个指标提取数据
    metrics_data = {}
    for metric, metric_name in metrics:
        task_labels = []
        v1_values = []
        v2_values = []
        
        for task_id in common_tasks:
            try:
                v1_val = float(v1_tasks[task_id].get(metric, 0))
                v2_val = float(v2_tasks[task_id].get(metric, 0))
                task_labels.append(task_id)
                v1_values.append(v1_val)
                v2_values.append(v2_val)
            except (ValueError, TypeError):
                continue
        
        if task_labels:
            metrics_data[metric] = {
                'task_labels': task_labels,
                'v1_values': v1_values,
                'v2_values': v2_values,
                'metric_name': metric_name
            }
    
    if not metrics_data:
        return None
    
    # 生成分析报告
    analysis_report = create_task_analysis_report(v1_data, v2_data, task_type, metrics, mode_name, model1_name, model2_name)
    
    # 保存分析报告
    report_file = os.path.join(output_dir, f"{task_type}_{mode_name.lower().replace(' ', '_')}_analysis_report.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(analysis_report)
    
    print(f"Generated analysis report: {report_file}")
    
    # 生成Python脚本
    script_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive PNG Chart Generator for {chart_title}
This script creates subplots for all metrics in one chart
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL not available, will create text-based chart")

import os
import math

def create_comprehensive_png_chart():
    """Create comprehensive PNG chart with subplots for all metrics"""
    
    if not PIL_AVAILABLE:
        print("PIL (Pillow) not available. Please install with: pip install Pillow")
        return False
    
    # Chart data
    metrics_data = {json.dumps(metrics_data, indent=4)}
    
    num_metrics = len(metrics_data)
    if num_metrics == 0:
        print("No data to chart")
        return False
    
    # Calculate subplot layout
    if num_metrics == 1:
        rows, cols = 1, 1
    elif num_metrics <= 2:
        rows, cols = 1, 2
    elif num_metrics <= 4:
        rows, cols = 2, 2
    elif num_metrics <= 6:
        rows, cols = 2, 3
    else:
        rows, cols = 3, 3
    
    # Image settings - adjusted for better title display
    subplot_width, subplot_height = 600, 400
    margin = 60
    title_height = 100  # Increased for better title space
    width = cols * subplot_width + (cols + 1) * margin
    height = rows * subplot_height + (rows + 1) * margin + title_height
    
    bg_color = (255, 255, 255)  # White background
    
    # Create image
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to load fonts
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)  # Reduced size
        subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)  # Reduced size
        label_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
    except:
        try:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            label_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        except:
            print("Could not load fonts")
            title_font = subtitle_font = label_font = small_font = None
    
    # Colors
    v1_color = (46, 134, 171)    # Blue for Model 1
    v2_color = (162, 59, 114)    # Purple for Model 2
    text_color = (51, 51, 51)     # Dark gray for text
    grid_color = (200, 200, 200)  # Light gray for grid
    
    # Main title - adjusted for better fit
    title_text = "{chart_title}"
    if title_font:
        # Split long titles into multiple lines
        if len(title_text) > 50:
            words = title_text.split()
            lines = []
            current_line = []
            for word in words:
                current_line.append(word)
                if len(' '.join(current_line)) > 40:
                    if len(current_line) > 1:
                        current_line.pop()
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(' '.join(current_line))
                        current_line = []
            if current_line:
                lines.append(' '.join(current_line))
            
            for i, line in enumerate(lines):
                title_bbox = draw.textbbox((0, 0), line, font=title_font)
                title_width = title_bbox[2] - title_bbox[0]
                title_x = (width - title_width) // 2
                draw.text((title_x, 15 + i * 30), line, fill=text_color, font=title_font)
        else:
            title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (width - title_width) // 2
            draw.text((title_x, 25), title_text, fill=text_color, font=title_font)
    
    # Draw subplots
    metric_idx = 0
    for row in range(rows):
        for col in range(cols):
            if metric_idx >= num_metrics:
                break
                
            metric = list(metrics_data.keys())[metric_idx]
            data = metrics_data[metric]
            
            task_labels = data['task_labels']
            v1_values = data['v1_values']
            v2_values = data['v2_values']
            metric_name = data['metric_name']
            
            # Calculate subplot position
            subplot_x = margin + col * (subplot_width + margin)
            subplot_y = title_height + margin + row * (subplot_height + margin)
            
            # Subplot area
            chart_left = subplot_x + 60
            chart_right = subplot_x + subplot_width - 20
            chart_top = subplot_y + 40
            chart_bottom = subplot_y + subplot_height - 60
            chart_width = chart_right - chart_left
            chart_height = chart_bottom - chart_top
            
            # Subplot title - truncate if too long
            display_title = metric_name
            if len(display_title) > 25:
                display_title = display_title[:22] + "..."
            
            if subtitle_font:
                subtitle_bbox = draw.textbbox((0, 0), display_title, font=subtitle_font)
                subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
                subtitle_x = subplot_x + (subplot_width - subtitle_width) // 2
                draw.text((subtitle_x, subplot_y + 5), display_title, fill=text_color, font=subtitle_font)
            
            # Find max value for this subplot
            max_value = max(max(v1_values) if v1_values else [0], max(v2_values) if v2_values else [0])
            if max_value == 0:
                max_value = 1
            
            # Draw grid lines
            for i in range(6):
                y = chart_bottom - (i * chart_height // 5)
                draw.line([(chart_left, y), (chart_right, y)], fill=grid_color, width=1)
                
                # Y-axis labels
                value = (i * max_value) / 5
                if small_font:
                    draw.text((chart_left - 50, y - 6), f"{{value:.2f}}", fill=text_color, font=small_font)
            
            # Calculate bar dimensions
            num_tasks = len(task_labels)
            if num_tasks > 0:
                bar_group_width = chart_width // num_tasks
                bar_width = max(8, bar_group_width // 3)
                bar_spacing = max(2, bar_width // 4)
                
                # Draw bars
                for i, (task_id, v1_val, v2_val) in enumerate(zip(task_labels, v1_values, v2_values)):
                    # Calculate positions
                    group_center = chart_left + (i + 0.5) * bar_group_width
                    
                    v1_bar_left = int(group_center - bar_width - bar_spacing//2)
                    v2_bar_left = int(group_center + bar_spacing//2)
                    
                    # Calculate heights
                    v1_height = int((v1_val / max_value) * chart_height)
                    v2_height = int((v2_val / max_value) * chart_height)
                    
                    # Draw bars
                    v1_bar_top = chart_bottom - v1_height
                    v2_bar_top = chart_bottom - v2_height
                    
                    # Model 1 bar
                    draw.rectangle([v1_bar_left, v1_bar_top, v1_bar_left + bar_width, chart_bottom], 
                                  fill=v1_color, outline=v1_color)
                    
                    # Model 2 bar
                    draw.rectangle([v2_bar_left, v2_bar_top, v2_bar_left + bar_width, chart_bottom], 
                                  fill=v2_color, outline=v2_color)
                    
                    # Task label (show all labels, rotate if needed)
                    if small_font:
                        label_x = group_center - len(task_id) * 2
                        draw.text((label_x, chart_bottom + 5), task_id, fill=text_color, font=small_font)
            
            # Y-axis label for this subplot
            if label_font:
                y_label = metric_name[:15] + "..." if len(metric_name) > 15 else metric_name
                draw.text((subplot_x + 5, chart_top + chart_height//2), y_label, fill=text_color, font=label_font)
            
            metric_idx += 1
    
    # Global legend
    legend_y = height - 40
    legend_x = margin
    
    # Model 1 legend
    draw.rectangle([legend_x, legend_y, legend_x + 20, legend_y + 15], fill=v1_color)
    if label_font:
        draw.text((legend_x + 30, legend_y), "{model1_name}", fill=text_color, font=label_font)
    
    # Model 2 legend
    legend_x += 150
    draw.rectangle([legend_x, legend_y, legend_x + 20, legend_y + 15], fill=v2_color)
    if label_font:
        draw.text((legend_x + 30, legend_y), "{model2_name}", fill=text_color, font=label_font)
    
    # Save image
    output_file = "{task_type}_{mode_name.lower().replace(' ', '_')}_comprehensive_comparison.png"
    img.save(output_file)
    print(f"Comprehensive PNG chart saved to: {{output_file}}")
    return True

if __name__ == "__main__":
    success = create_comprehensive_png_chart()
    if not success:
        print("Failed to create comprehensive PNG chart")
'''
    
    # 保存Python脚本
    script_file = os.path.join(output_dir, f"{task_type}_{mode_name.lower().replace(' ', '_')}_comprehensive_png_generator.py")
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"Generated comprehensive PNG script: {script_file}")
    return script_file

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Model Performance Comparison Toolkit')
    parser.add_argument('--model1-name', required=True, help='Name of the first model (e.g., Dolphin-1.6)')
    parser.add_argument('--model2-name', required=True, help='Name of the second model (e.g., Dolphin-1.9)')
    parser.add_argument('--model1-standard-dir', required=True, help='Directory containing model1 standard mode results')
    parser.add_argument('--model1-deep-dir', help='Directory containing model1 deep reasoning mode results')
    parser.add_argument('--model2-standard-dir', required=True, help='Directory containing model2 standard mode results')
    parser.add_argument('--model2-deep-dir', help='Directory containing model2 deep reasoning mode results')
    parser.add_argument('--output-dir', help='Output directory (default: auto-generated)')
    parser.add_argument('--include-deep', action='store_true', help='Include deep reasoning mode comparison')
    
    args = parser.parse_args()
    
    print(f"=== Model Performance Comparison Toolkit ===")
    print(f"Comparing {args.model1_name} vs {args.model2_name}")
    
    # 创建输出目录
    if args.output_dir:
        output_dir = args.output_dir
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_model1 = args.model1_name.replace(' ', '_').replace('.', '_')
        safe_model2 = args.model2_name.replace(' ', '_').replace('.', '_')
        output_dir = f"{safe_model1}_vs_{safe_model2}_Analysis_{timestamp}"
    
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")
    
    # 创建子目录
    charts_dir = os.path.join(output_dir, "charts")
    reports_dir = os.path.join(output_dir, "reports")
    data_dir = os.path.join(output_dir, "data")
    scripts_dir = os.path.join(output_dir, "scripts")
    
    for subdir in [charts_dir, reports_dir, data_dir, scripts_dir]:
        os.makedirs(subdir, exist_ok=True)
    
    print("\n1. Loading data...")
    
    # 加载所有数据
    data_standard = {'model1': {}, 'model2': {}}
    data_deep = {'model1': {}, 'model2': {}}
    
    for task in ['cla', 'mea', 'seg', 'report']:
        # Standard mode
        data_standard['model1'][task] = load_results_txt(os.path.join(args.model1_standard_dir, f"{task}_results.txt"))
        data_standard['model2'][task] = load_results_txt(os.path.join(args.model2_standard_dir, f"{task}_results.txt"))
        
        # Deep mode (if available)
        if args.include_deep and args.model1_deep_dir and args.model2_deep_dir:
            data_deep['model1'][task] = load_results_txt(os.path.join(args.model1_deep_dir, f"{task}_results.txt"))
            data_deep['model2'][task] = load_results_txt(os.path.join(args.model2_deep_dir, f"{task}_results.txt"))
    
    print("\n2. Generating comprehensive task charts with subplots...")
    
    # 定义所有任务和指标 (移除failed_items)
    task_metrics = {
        'classification': [
            ('acc', 'Accuracy'),
            ('precision', 'Precision'),
            ('recall', 'Recall'),
            ('f1', 'F1-Score')
        ],
        'measurement': [
            ('RMSE', 'Root Mean Square Error'),
            ('MAE', 'Mean Absolute Error'),
            ('%_within_tolerance', 'Percentage within Tolerance')
        ],
        'segmentation': [
            ('acc', 'Accuracy')
        ],
        'report': [
            ('Bleu-1', 'BLEU-1'),
            ('Bleu-2', 'BLEU-2'),
            ('Bleu-3', 'BLEU-3'),
            ('Bleu-4', 'BLEU-4'),
            ('Rouge', 'Rouge'),
            ('BERTScore', 'BERTScore')
        ]
    }
    
    generated_scripts = []
    
    # 生成标准模式的任务图表
    print("\nGenerating Standard Mode comprehensive charts...")
    for task_type, metrics in task_metrics.items():
        print(f"  Processing {task_type} task...")
        script_file = generate_task_subplot_png_script(
            data_standard, task_type, metrics, "Standard Mode", scripts_dir, args.model1_name, args.model2_name
        )
        if script_file:
            generated_scripts.append(script_file)
    
    # 生成深度推理模式的任务图表
    if args.include_deep and args.model1_deep_dir and args.model2_deep_dir:
        print("\nGenerating Deep Reasoning Mode comprehensive charts...")
        for task_type, metrics in task_metrics.items():
            print(f"  Processing {task_type} task...")
            script_file = generate_task_subplot_png_script(
                data_deep, task_type, metrics, "Deep Reasoning Mode", scripts_dir, args.model1_name, args.model2_name
            )
            if script_file:
                generated_scripts.append(script_file)
    
    # 复制原始数据到data目录
    print("\n3. Copying original data files...")
    
    data_sources = [
        (args.model1_standard_dir, "model1_standard"),
        (args.model2_standard_dir, "model2_standard")
    ]
    
    if args.include_deep and args.model1_deep_dir and args.model2_deep_dir:
        data_sources.extend([
            (args.model1_deep_dir, "model1_deep"),
            (args.model2_deep_dir, "model2_deep")
        ])
    
    for source_dir, label in data_sources:
        target_subdir = os.path.join(data_dir, label)
        os.makedirs(target_subdir, exist_ok=True)
        
        for task in ['cla', 'mea', 'seg', 'report']:
            source_file = os.path.join(source_dir, f"{task}_results.txt")
            if os.path.exists(source_file):
                target_file = os.path.join(target_subdir, f"{task}_results.txt")
                shutil.copy2(source_file, target_file)
                print(f"  Copied {source_file} -> {target_file}")
    
    # 创建批量运行脚本
    batch_script = f"""#!/bin/bash
# Comprehensive PNG Generator for Model Comparison

echo "=== Generating Comprehensive Model Comparison Charts ==="
echo "Comparing {args.model1_name} vs {args.model2_name}"
echo "Output directory: {output_dir}"

cd "{scripts_dir}"

# Check if PIL is available
python3 -c "from PIL import Image; print('PIL available')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "PIL (Pillow) is available, generating comprehensive PNG charts..."
    
    # Run all comprehensive PNG generators
"""
    
    for script_file in generated_scripts:
        script_name = os.path.basename(script_file)
        batch_script += f"    echo \"Generating {script_name}...\"\n"
        batch_script += f"    python3 {script_name}\n"
        batch_script += f"    mv *.png ../{os.path.basename(charts_dir)}/\n"
    
    batch_script += f"""
    echo "All comprehensive charts generated!"
    echo "Generated $(ls -1 ../{os.path.basename(charts_dir)}/*.png 2>/dev/null | wc -l) PNG files"
    ls -la ../{os.path.basename(charts_dir)}/*.png 2>/dev/null
else
    echo "PIL (Pillow) not available. Please install with:"
    echo "pip install Pillow"
fi

echo "Done!"
"""
    
    batch_file = os.path.join(output_dir, "generate_all_charts.sh")
    with open(batch_file, 'w', encoding='utf-8') as f:
        f.write(batch_script)
    
    # 使脚本可执行
    os.chmod(batch_file, 0o755)
    
    # 创建主报告
    modes_text = "Standard Mode"
    if args.include_deep:
        modes_text += " and Deep Reasoning Mode"
    
    main_report = f"""# {args.model1_name} vs {args.model2_name} Performance Comparison

## Overview

This analysis compares the performance of **{args.model1_name}** and **{args.model2_name}** across four key tasks in {modes_text}.

## Key Improvements

✅ **Complete Dataset Labels**: All task IDs shown on x-axis  
✅ **Subplot Organization**: Each task has all metrics in one chart  
✅ **Comprehensive Integration**: Charts, reports, data, and scripts in one folder  
✅ **Measurement Task Fix**: Removed failed_items metric  
✅ **Title Optimization**: Fixed title overflow issues  
✅ **Command Line Tool**: Extensible for testing other models  

## Directory Structure

```
{os.path.basename(output_dir)}/
├── charts/           # PNG chart files
├── reports/          # Analysis reports (.md files)
├── data/            # Original data files
│   ├── model1_standard/
│   ├── model2_standard/
{"│   ├── model1_deep/" if args.include_deep else ""}
{"│   └── model2_deep/" if args.include_deep else ""}
└── scripts/         # Python generation scripts
```

## Generated Charts

### Task-Based Comprehensive Charts
Each chart contains subplots for all metrics of that task:

#### Standard Mode
- `classification_standard_mode_comprehensive_comparison.png`
- `measurement_standard_mode_comprehensive_comparison.png` (3 metrics: RMSE, MAE, % within tolerance)
- `segmentation_standard_mode_comprehensive_comparison.png`
- `report_standard_mode_comprehensive_comparison.png`

{"#### Deep Reasoning Mode" if args.include_deep else ""}
{"- `classification_deep_reasoning_mode_comprehensive_comparison.png`" if args.include_deep else ""}
{"- `measurement_deep_reasoning_mode_comprehensive_comparison.png`" if args.include_deep else ""}
{"- `segmentation_deep_reasoning_mode_comprehensive_comparison.png`" if args.include_deep else ""}
{"- `report_deep_reasoning_mode_comprehensive_comparison.png`" if args.include_deep else ""}

## Usage

### Generate All Charts
```bash
./generate_all_charts.sh
```

### Chart Specifications
- **Format**: PNG
- **Layout**: Subplots for each metric within task
- **X-axis**: Complete task ID labels
- **Colors**: {args.model1_name} (Blue) vs {args.model2_name} (Purple)
- **Resolution**: High-resolution for publication quality

## Command Line Usage

This toolkit can be used to compare any two models:

```bash
python3 model_comparison_toolkit.py \\
    --model1-name "Model A" \\
    --model2-name "Model B" \\
    --model1-standard-dir /path/to/model1/standard \\
    --model2-standard-dir /path/to/model2/standard \\
    --model1-deep-dir /path/to/model1/deep \\
    --model2-deep-dir /path/to/model2/deep \\
    --include-deep \\
    --output-dir custom_output_dir
```

---

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
Models: {args.model1_name} vs {args.model2_name}  
Total Charts: {len(generated_scripts)}  
"""
    
    main_report_file = os.path.join(output_dir, "README.md")
    with open(main_report_file, 'w', encoding='utf-8') as f:
        f.write(main_report)
    
    print(f"\n{'='*80}")
    print("Model comparison analysis setup completed!")
    print(f"Main directory: {output_dir}")
    print(f"Generated {len(generated_scripts)} comprehensive chart scripts")
    print(f"Total charts to be generated: {len(generated_scripts)}")
    
    print(f"\n📁 Directory structure:")
    print(f"  📊 charts/     - PNG chart files")
    print(f"  📋 reports/    - Analysis reports")
    print(f"  📁 data/       - Original data files")
    print(f"  🔧 scripts/    - Generation scripts")
    
    print(f"\n🎯 To generate all charts:")
    print(f"1. cd {output_dir}")
    print(f"2. ./generate_all_charts.sh")
    
    print(f"\n✨ Key improvements:")
    print(f"  ✅ Removed failed_items from measurement task")
    print(f"  ✅ Fixed title overflow for report and segmentation tasks")
    print(f"  ✅ Command line interface for extensibility")
    print(f"  ✅ Complete dataset labels on x-axis")
    print(f"  ✅ Subplots for all metrics per task")

if __name__ == "__main__":
    main() 