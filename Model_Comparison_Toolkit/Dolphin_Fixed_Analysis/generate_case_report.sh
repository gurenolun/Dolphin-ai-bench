#!/bin/bash

# Dolphin三案例对比报告生成脚本
# 生成DolphinV1.9标准模式与深度推理模式的三案例对比报告
# 注意：请先运行 conda activate multimodal_test

echo "=== Dolphin三案例对比报告生成器 ===="
echo "正在生成DolphinV1.9标准模式与深度推理模式的对比报告..."
echo ""

# 检查是否在正确的conda环境中
if [[ "$CONDA_DEFAULT_ENV" != "multimodal_test" ]]; then
    echo "⚠️  警告: 当前不在multimodal_test环境中"
    echo "请先运行: conda activate multimodal_test"
    echo ""
fi

# 检查scripts目录是否存在
if [ ! -d "scripts" ]; then
    echo "错误: scripts目录不存在"
    exit 1
fi

# 检查Python脚本是否存在
if [ ! -f "scripts/generate_three_case_comparison_final.py" ]; then
    echo "错误: generate_three_case_comparison_final.py不存在"
    exit 1
fi

# 进入scripts目录
cd scripts

# 激活conda环境并运行Python脚本
echo "正在运行三案例对比程序..."
python3 generate_three_case_comparison_final.py

# 检查运行结果
if [ $? -eq 0 ]; then
    echo ""
    echo "=== 报告生成完成 ==="
    echo "生成的报告文件:"
    
    if [ -f "DolphinV1.9_三案例对比报告.md" ]; then
        echo "  ✅ scripts/DolphinV1.9_三案例对比报告.md"
        
        # 复制到reports目录
        if [ -d "../reports" ]; then
            cp "DolphinV1.9_三案例对比报告.md" "../reports/"
            echo "  ✅ reports/DolphinV1.9_三案例对比报告.md (已复制)"
        fi
    fi
    
    echo ""
    echo "📊 报告内容包括:"
    echo "  - 三个具体案例的详细对比"
    echo "  - 标准模式(DolphinV1.9p) vs 深度推理模式(DolphinV1.9)"
    echo "  - 图片路径、参考答案和模型回复"
    echo "  - 准确性分析和回复长度对比"
    echo ""
    echo "🎉 所有任务完成！"
else
    echo ""
    echo "❌ 报告生成失败"
    echo "请检查:"
    echo "  1. multimodal_test环境是否正确安装"
    echo "  2. 数据路径是否正确"
    echo "  3. 是否有足够的权限"
fi 