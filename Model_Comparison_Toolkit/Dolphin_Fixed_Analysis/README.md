# Dolphin Performance Analysis Toolkit

## Overview

This toolkit provides comprehensive analysis tools for Dolphin model performance comparison, including **Dolphin-1.6 vs Dolphin-1.9** comparison and detailed **DolphinV1.9 three-case analysis**.

## Key Features

✅ **Complete Dataset Labels**: All task IDs shown on x-axis  
✅ **Subplot Organization**: Each task has all metrics in one chart  
✅ **Comprehensive Integration**: Charts, reports, data, and scripts in one folder  
✅ **Measurement Task Fix**: Removed failed_items metric  
✅ **Title Optimization**: Fixed title overflow issues  
✅ **Command Line Tool**: Extensible for testing other models  
✅ **Three-Case Comparison**: Detailed case-by-case analysis tool for DolphinV1.9  

## Directory Structure

```
Dolphin_Fixed_Analysis/
├── charts/           # PNG chart files
├── reports/          # Analysis reports (.md files)
├── data/             # Raw comparison data
├── scripts/          # Analysis and generation scripts
├── generate_case_report.sh    # Three-case comparison script
└── README.md         # This file
```

## Quick Start

### 1. Three-Case Comparison (DolphinV1.9)

Generate detailed comparison between **DolphinV1.9p (Standard)** and **DolphinV1.9 (Deep Reasoning)** modes:

```bash
# Method 1: Direct script execution
./generate_case_report.sh

# Method 2: Manual execution
cd scripts
conda activate multimodal_test
python3 generate_three_case_comparison_final.py
```

**Output**: `DolphinV1.9_三案例对比报告.md` containing:
- **Case 1**: Ultrasound position identification (Task 48)
- **Case 2**: Thyroid nodule segmentation (Task 31)  
- **Case 3**: Fetal ultrasound plane classification (Task 03)

Each case includes:
- Image path and reference answer
- Standard mode response (DolphinV1.9p)
- Deep reasoning mode response (DolphinV1.9)
- Accuracy analysis and response length comparison
