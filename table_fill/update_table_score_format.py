#!/usr/bin/env python3
import pandas as pd
import numpy as np
import re

# 读取最新结果文件
cla_results = pd.read_csv('/home/guohongcheng/DolphinV1.9p_results/cla_results.txt', sep='\t')
seg_results = pd.read_csv('/home/guohongcheng/DolphinV1.9p_results/seg_results.txt', sep='\t')
mea_results = pd.read_csv('/home/guohongcheng/DolphinV1.9p_results/mea_results.txt', sep='\t')
report_results = pd.read_csv('/home/guohongcheng/DolphinV1.9p_results/report_results.txt', sep='\t')

# 将所有任务ID转换为字符串
cla_results['task_id'] = cla_results['task_id'].astype(str)
seg_results['task_id'] = seg_results['task_id'].astype(str)
mea_results['task_id'] = mea_results['task_id'].astype(str)
report_results['task_id'] = report_results['task_id'].astype(str)

# 定义任务和数据集的对应关系
diag_datasets = ['21', '23', '25', '28_1', '32', '40', '42', '44', '57', '66', '70', '74is_normal', '75']
vra_datasets = ['03', '10', '18', '28', '37', '50', '53', '69', '74is_visible', 'anatomy']
ll_datasets = ['04', '17', '23', '32', '64']
od_datasets = ['09', '13', '16', '18', '31', '37', '38', '47', '49', '50', '52', '53', '67']
kd_datasets = ['48']
cve_datasets = ['18', '27', '31', '50', '57']
rg_datasets = ['39']
cg_datasets = ['10', '44']

# 获取所有模型列表
all_models = sorted(list(set(cla_results['model'].unique()).union(
    seg_results['model'].unique(),
    mea_results['model'].unique(),
    report_results['model'].unique()
)))

# 确保所有 GPT-4o 相关模型都被正确处理
models = []
for model in all_models:
    # 跳过可能的重复模型名称变体和local_model
    if model == 'gpt-4o' and ('gpt-4o-mini' in all_models or 'gpt-4o-2024-08-06' in all_models):
        print(f"注意: 发现基础模型 'gpt-4o'，将与其他 GPT-4o 变体一起处理")
    elif model == 'local_model':
        print(f"注意: 跳过 'local_model'")
    else:
        models.append(model)

# 处理 gpt-4o 的特殊情况
gpt4o_base_exists = 'gpt-4o' in all_models
gpt4o_mini_exists = 'gpt-4o-mini' in all_models
gpt4o_dated_exists = 'gpt-4o-2024-08-06' in all_models

if gpt4o_base_exists:
    print(f"发现 'gpt-4o' 模型数据")

# 创建结果字典
results = {}

# 创建排名字典
rankings = {}

# 初始化排名字典
for task in ['diag', 'vra', 'll', 'od', 'kd', 'cve', 'rg', 'cg']:
    rankings[task] = {}
    
# 处理所有任务的数据
for model in models:
    results[model] = {}
    
    # Diag - 诊断任务
    diag_data = cla_results[cla_results['task_id'].isin(diag_datasets) & (cla_results['model'] == model)]
    if not diag_data.empty:
        results[model]['diag_acc'] = diag_data['acc'].mean()
        results[model]['diag_f1'] = diag_data['f1'].mean()
    else:
        results[model]['diag_acc'] = 0.0
        results[model]['diag_f1'] = 0.0
    
    # VRA - 视图识别任务
    vra_data = cla_results[cla_results['task_id'].isin(vra_datasets) & (cla_results['model'] == model)]
    if not vra_data.empty:
        results[model]['vra_acc'] = vra_data['acc'].mean()
        results[model]['vra_f1'] = vra_data['f1'].mean()
    else:
        results[model]['vra_acc'] = 0.0
        results[model]['vra_f1'] = 0.0

    # LL - 病灰定位任务
    ll_data = seg_results[seg_results['task_id'].isin([d for d in ll_datasets if d in seg_results['task_id'].unique()]) & 
                         (seg_results['model'] == model)]
    if not ll_data.empty:
        results[model]['ll_acc'] = ll_data['acc'].mean()
    else:
        results[model]['ll_acc'] = 0.0
    
    # OD - 目标检测任务
    od_data = seg_results[seg_results['task_id'].isin([d for d in od_datasets if d in seg_results['task_id'].unique()]) & 
                         (seg_results['model'] == model)]
    if not od_data.empty:
        results[model]['od_acc'] = od_data['acc'].mean()
    else:
        results[model]['od_acc'] = 0.0
    
    # KD - 关键点检测任务
    kd_data = seg_results[seg_results['task_id'].isin([d for d in kd_datasets if d in seg_results['task_id'].unique()]) & 
                         (seg_results['model'] == model)]
    if not kd_data.empty:
        results[model]['kd_acc'] = kd_data['acc'].mean()
    else:
        results[model]['kd_acc'] = 0.0
    
    # CVE - 连续值估计任务
    cve_data = mea_results[mea_results['task_id'].isin([d for d in cve_datasets if d in mea_results['task_id'].unique()]) & 
                          (mea_results['model'] == model)]
    if not cve_data.empty:
        # 处理可能的 NaN 值
        rmse_values = cve_data['RMSE'].replace([np.inf, -np.inf], np.nan).dropna()
        std_values = cve_data['Std'].replace([np.inf, -np.inf], np.nan).dropna()
        tol_values = cve_data['%_within_tolerance'].replace([np.inf, -np.inf], np.nan).dropna()
        
        results[model]['cve_rmse'] = rmse_values.mean() if not rmse_values.empty else 0.0
        results[model]['cve_std'] = std_values.mean() if not std_values.empty else 0.0
        results[model]['cve_tol'] = tol_values.mean() if not tol_values.empty else 0.0
    else:
        results[model]['cve_rmse'] = 0.0
        results[model]['cve_std'] = 0.0
        results[model]['cve_tol'] = 0.0
    
    # RG - 报告生成任务
    rg_data = report_results[report_results['task_id'].isin([d for d in rg_datasets if d in report_results['task_id'].unique()]) & 
                            (report_results['model'] == model)]
    if not rg_data.empty:
        results[model]['rg_bleu'] = rg_data['Bleu-4'].mean() if 'Bleu-4' in rg_data.columns and not rg_data['Bleu-4'].isna().all() else 0.0
        results[model]['rg_rouge'] = rg_data['Rouge'].mean() if 'Rouge' in rg_data.columns and not rg_data['Rouge'].isna().all() else 0.0
        results[model]['rg_bert'] = rg_data['BERTScore'].mean() if 'BERTScore' in rg_data.columns and not rg_data['BERTScore'].isna().all() else 0.0
    else:
        # 检查是否是 gpt-4o-mini 或 gpt-4o-2024-08-06，如果是，尝试从 gpt-4o 获取数据
        if model in ['gpt-4o-mini', 'gpt-4o-2024-08-06'] and gpt4o_base_exists:
            gpt4o_rg_data = report_results[report_results['task_id'].isin([d for d in rg_datasets if d in report_results['task_id'].unique()]) & 
                                        (report_results['model'] == 'gpt-4o')]
            if not gpt4o_rg_data.empty:
                print(f"为 {model} 使用 gpt-4o 的报告生成数据")
                results[model]['rg_bleu'] = gpt4o_rg_data['Bleu-4'].mean() if 'Bleu-4' in gpt4o_rg_data.columns and not gpt4o_rg_data['Bleu-4'].isna().all() else 0.0
                results[model]['rg_rouge'] = gpt4o_rg_data['Rouge'].mean() if 'Rouge' in gpt4o_rg_data.columns and not gpt4o_rg_data['Rouge'].isna().all() else 0.0
                results[model]['rg_bert'] = gpt4o_rg_data['BERTScore'].mean() if 'BERTScore' in gpt4o_rg_data.columns and not gpt4o_rg_data['BERTScore'].isna().all() else 0.0
            else:
                results[model]['rg_bleu'] = 0.0
                results[model]['rg_rouge'] = 0.0
                results[model]['rg_bert'] = 0.0
        else:
            results[model]['rg_bleu'] = 0.0
            results[model]['rg_rouge'] = 0.0
            results[model]['rg_bert'] = 0.0
    
    # CG - 标题生成任务
    cg_data = report_results[report_results['task_id'].isin([d for d in cg_datasets if d in report_results['task_id'].unique()]) & 
                            (report_results['model'] == model)]
    if not cg_data.empty:
        results[model]['cg_bleu'] = cg_data['Bleu-4'].mean() if 'Bleu-4' in cg_data.columns and not cg_data['Bleu-4'].isna().all() else 0.0
        results[model]['cg_rouge'] = cg_data['Rouge'].mean() if 'Rouge' in cg_data.columns and not cg_data['Rouge'].isna().all() else 0.0
        results[model]['cg_bert'] = cg_data['BERTScore'].mean() if 'BERTScore' in cg_data.columns and not cg_data['BERTScore'].isna().all() else 0.0
    else:
        # 检查是否是 gpt-4o-mini 或 gpt-4o-2024-08-06，如果是，尝试从 gpt-4o 获取数据
        if model in ['gpt-4o-mini', 'gpt-4o-2024-08-06'] and gpt4o_base_exists:
            gpt4o_cg_data = report_results[report_results['task_id'].isin([d for d in cg_datasets if d in report_results['task_id'].unique()]) & 
                                        (report_results['model'] == 'gpt-4o')]
            if not gpt4o_cg_data.empty:
                print(f"为 {model} 使用 gpt-4o 的标题生成数据")
                results[model]['cg_bleu'] = gpt4o_cg_data['Bleu-4'].mean() if 'Bleu-4' in gpt4o_cg_data.columns and not gpt4o_cg_data['Bleu-4'].isna().all() else 0.0
                results[model]['cg_rouge'] = gpt4o_cg_data['Rouge'].mean() if 'Rouge' in gpt4o_cg_data.columns and not gpt4o_cg_data['Rouge'].isna().all() else 0.0
                results[model]['cg_bert'] = gpt4o_cg_data['BERTScore'].mean() if 'BERTScore' in gpt4o_cg_data.columns and not gpt4o_cg_data['BERTScore'].isna().all() else 0.0
            else:
                results[model]['cg_bleu'] = 0.0
                results[model]['cg_rouge'] = 0.0
                results[model]['cg_bert'] = 0.0
        else:
            results[model]['cg_bleu'] = 0.0
            results[model]['cg_rouge'] = 0.0
            results[model]['cg_bert'] = 0.0
            
# 计算每个模型的得分
for model in models:
    # 定义任务权重，与 calculate_u2_scores.py 中保持一致
    weights = {
        'diag': 0.2,
        'vra': 0.2,
        'll': 0.07,
        'od': 0.27,
        'kd': 0.07,
        'cve': 0.07,
        'rg': 0.08,
        'cg': 0.04
    }
    
    # 保存原始指标值，不进行得分计算
    # 诊断任务 (DD)
    results[model]['task1_acc'] = results[model]['diag_acc']
    results[model]['task1_f1'] = results[model]['diag_f1']
    
    # 视图识别任务 (VRA)
    results[model]['task2_acc'] = results[model]['vra_acc']
    results[model]['task2_f1'] = results[model]['vra_f1']
    
    # 病灰定位任务 (LL)
    results[model]['task3_acc'] = results[model]['ll_acc']
    
    # 目标检测任务 (OD)
    results[model]['task4_acc'] = results[model]['od_acc']
    
    # 关键点检测任务 (KD)
    results[model]['task5_acc'] = results[model]['kd_acc']
    
    # 连续值估计任务 (CVE)
    results[model]['task6_rmse'] = results[model]['cve_rmse']
    results[model]['task6_std'] = results[model]['cve_std']
    results[model]['task6_tol'] = results[model]['cve_tol']
    
    # 报告生成任务 (RG)
    results[model]['task7_bleu'] = results[model]['rg_bleu']
    results[model]['task7_rouge'] = results[model]['rg_rouge']
    results[model]['task7_bert'] = results[model]['rg_bert']
    
    # 标题生成任务 (CG)
    results[model]['task8_bleu'] = results[model]['cg_bleu']
    results[model]['task8_rouge'] = results[model]['cg_rouge']
    results[model]['task8_bert'] = results[model]['cg_bert']
    
    # 根据 calculate_u2_scores.py 的逻辑计算总得分
    # 计算各任务得分
    task_scores = {
        'diag': results[model]['task1_acc'],
        'vra': results[model]['task2_acc'],
        'll': results[model]['task3_acc'],
        'od': results[model]['task4_acc'],
        'kd': results[model]['task5_acc'],
        'cve': 1 - results[model]['task6_rmse'],  # 使用 1-RMSE
        'rg': results[model]['task7_bleu'] / 100.0,  # BLEU-4通常是百分比，需要归一化
        'cg': results[model]['task8_bleu'] / 100.0   # BLEU-4通常是百分比，需要归一化
    }
    
    # 确保所有分数在 0~1 之间
    for task in task_scores:
        task_scores[task] = max(0.0, min(1.0, task_scores[task]))
    
    # 计算加权总分
    total_score = sum(weights[task] * task_scores[task] for task in weights)
    
    # 保存总得分
    results[model]['score'] = round(total_score, 4)

# 打印模型得分
print("\n模型得分:")
for model in sorted(models, key=lambda m: results[m]['score'], reverse=True):
    print(f"{model}: 得分 {results[model]['score']:.4f}")

# 创建新的表格内容
table_content = ""

# 打印所有模型名称，以便我们了解结果字典中的模型名称格式
print("所有模型名称:")
for model_name in sorted(results.keys()):
    print(f"- {model_name}")

# 添加随机猜测基线
table_content += "Random Guessing & 0.4143 & 0.4135 & 0.3195 & 0.3184 & 0.1118 & 0.0680 & 0.1120 & 0.5472 & 0.2962 & - & - & - & - & - & - & - & 0.2125 \\\\\n\\midrule\n"

# 添加医疗专用开源模型部分
table_content += "\\multicolumn{18}{c}{\\textit{Medical-Specific Open-Source Models}} \\\\\n\\midrule\n"

# 添加医疗专用开源模型（如果有数据）
medical_models = ['MiniGPT-Med', 'MedDr']
for model in medical_models:
    if model in models:
        # 构建模型行
        row = f"{model} & "
        
        # 诊断 (DD)
        diag_acc_str = f"{results[model]['task1_acc']:.4f}"
        diag_f1_str = f"{results[model]['task1_f1']:.4f}"
        row += f"{diag_acc_str} & {diag_f1_str} & "
        
        # 视图识别 (VRA)
        vra_acc_str = f"{results[model]['task2_acc']:.4f}"
        vra_f1_str = f"{results[model]['task2_f1']:.4f}"
        row += f"{vra_acc_str} & {vra_f1_str} & "
        
        # 病灰定位 (LL)
        ll_acc_str = f"{results[model]['task3_acc']:.4f}"
        row += f"{ll_acc_str} & "
        
        # 目标检测 (OD)
        od_acc_str = f"{results[model]['task4_acc']:.4f}"
        row += f"{od_acc_str} & "
        
        # 关键点检测 (KD)
        kd_acc_str = f"{results[model]['task5_acc']:.4f}"
        row += f"{kd_acc_str} & "
        
        # 连续值估计 (CVE)
        cve_rmse_str = f"{results[model]['task6_rmse']:.4f}"
        cve_std_str = f"{results[model]['task6_std']:.4f}"
        cve_tol_str = f"{results[model]['task6_tol']:.4f}"
        row += f"{cve_rmse_str} & {cve_std_str} & {cve_tol_str} & "
        
        # 报告生成 (RG)
        rg_bleu_str = f"{results[model]['task7_bleu']:.4f}"
        rg_rouge_str = f"{results[model]['task7_rouge']:.4f}"
        rg_bert_str = f"{results[model]['task7_bert']:.4f}"
        row += f"{rg_bleu_str} & {rg_rouge_str} & {rg_bert_str} & "
        
        # 标题生成 (CG)
        cg_bleu_str = f"{results[model]['task8_bleu']:.4f}"
        cg_rouge_str = f"{results[model]['task8_rouge']:.4f}"
        cg_bert_str = f"{results[model]['task8_bert']:.4f}"
        row += f"{cg_bleu_str} & {cg_rouge_str} & {cg_bert_str} & "
        
        # 得分
        score_str = f"{results[model]['score']:.4f}"
        row += f"{score_str} \\\\"
        
        table_content += row + "\n"

# 添加开源模型部分
table_content += "\\midrule\n\\multicolumn{18}{c}{\\textit{Open-Source Multimodal Models}} \\\\\n\\midrule\n"

# 定义开源模型列表
open_source_models = [m for m in models if not any(closed_name in m.lower() for closed_name in ['gpt', 'gemini', 'claude', 'doubao']) 
                    and m not in medical_models]

# 根据原始数据计算这三个模型的结果
for model in ['Qwen-2.5-VL-7B', 'Qwen-2.5-VL-32B-Instruct', 'Qwen-2.5-VL-72B-Instruct']:
    if model in results:
        # 构建模型行
        row = f"{model} & "
        
        # 诊断 (DD)
        diag_acc_str = f"{results[model]['task1_acc']:.4f}"
        diag_f1_str = f"{results[model]['task1_f1']:.4f}"
        row += f"{diag_acc_str} & {diag_f1_str} & "
        
        # 视图识别 (VRA)
        vra_acc_str = f"{results[model]['task2_acc']:.4f}"
        vra_f1_str = f"{results[model]['task2_f1']:.4f}"
        row += f"{vra_acc_str} & {vra_f1_str} & "
        
        # 病灰定位 (LL)
        ll_acc_str = f"{results[model]['task3_acc']:.4f}"
        row += f"{ll_acc_str} & "
        
        # 目标检测 (OD)
        od_acc_str = f"{results[model]['task4_acc']:.4f}"
        row += f"{od_acc_str} & "
        
        # 关键点检测 (KD)
        kd_acc_str = f"{results[model]['task5_acc']:.4f}"
        row += f"{kd_acc_str} & "
        
        # 连续值估计 (CVE)
        cve_rmse_str = f"{results[model]['task6_rmse']:.4f}"
        cve_std_str = f"{results[model]['task6_std']:.4f}"
        cve_tol_str = f"{results[model]['task6_tol']:.4f}"
        row += f"{cve_rmse_str} & {cve_std_str} & {cve_tol_str} & "
        
        # 报告生成 (RG)
        rg_bleu_str = f"{results[model]['task7_bleu']:.4f}"
        rg_rouge_str = f"{results[model]['task7_rouge']:.4f}"
        rg_bert_str = f"{results[model]['task7_bert']:.4f}"
        row += f"{rg_bleu_str} & {rg_rouge_str} & {rg_bert_str} & "
        
        # 标题生成 (CG)
        cg_bleu_str = f"{results[model]['task8_bleu']:.4f}"
        cg_rouge_str = f"{results[model]['task8_rouge']:.4f}"
        cg_bert_str = f"{results[model]['task8_bert']:.4f}"
        row += f"{cg_bleu_str} & {cg_rouge_str} & {cg_bert_str} & "
        
        # 得分
        score_str = f"{results[model]['score']:.4f}"
        row += f"{score_str} \\\\"
        
        table_content += row + "\n"
    else:
        print(f"\u6a21\u578b {model} \u5728\u7ed3\u679c\u4e2d\u4e0d\u5b58\u5728\uff0c\u8df3\u8fc7")

# 对其他开源模型按得分排序
other_open_source_models = [m for m in open_source_models if m not in ['Qwen-2.5-VL-7B', 'Qwen-2.5-VL-32B-Instruct', 'Qwen-2.5-VL-72B-Instruct']]
other_open_source_models.sort(key=lambda m: results[m]['score'], reverse=True)

# 获取开源模型中得分前三的模型
top3_open_source = sorted(open_source_models, key=lambda m: results[m]['score'], reverse=True)[:3]

for model in other_open_source_models:
    # 构建模型行
    row = f"{model} & "
    
    # 诊断 (DD)
    diag_acc_str = f"{results[model]['task1_acc']:.4f}"
    diag_f1_str = f"{results[model]['task1_f1']:.4f}"
    row += f"{diag_acc_str} & {diag_f1_str} & "
    
    # 视图识别 (VRA)
    vra_acc_str = f"{results[model]['task2_acc']:.4f}"
    vra_f1_str = f"{results[model]['task2_f1']:.4f}"
    row += f"{vra_acc_str} & {vra_f1_str} & "
    
    # 病灰定位 (LL)
    ll_acc_str = f"{results[model]['task3_acc']:.4f}"
    row += f"{ll_acc_str} & "
    
    # 目标检测 (OD)
    od_acc_str = f"{results[model]['task4_acc']:.4f}"
    row += f"{od_acc_str} & "
    
    # 关键点检测 (KD)
    kd_acc_str = f"{results[model]['task5_acc']:.4f}"
    row += f"{kd_acc_str} & "
    
    # 连续值估计 (CVE)
    cve_rmse_str = f"{results[model]['task6_rmse']:.4f}"
    cve_std_str = f"{results[model]['task6_std']:.4f}"
    cve_tol_str = f"{results[model]['task6_tol']:.4f}"
    row += f"{cve_rmse_str} & {cve_std_str} & {cve_tol_str} & "
    
    # 报告生成 (RG)
    rg_bleu_str = f"{results[model]['task7_bleu']:.4f}"
    rg_rouge_str = f"{results[model]['task7_rouge']:.4f}"
    rg_bert_str = f"{results[model]['task7_bert']:.4f}"
    row += f"{rg_bleu_str} & {rg_rouge_str} & {rg_bert_str} & "
    
    # 标题生成 (CG)
    cg_bleu_str = f"{results[model]['task8_bleu']:.4f}"
    cg_rouge_str = f"{results[model]['task8_rouge']:.4f}"
    cg_bert_str = f"{results[model]['task8_bert']:.4f}"
    row += f"{cg_bleu_str} & {cg_rouge_str} & {cg_bert_str} & "
    
    # 得分
    score_str = f"{results[model]['score']:.4f}"
    row += f"{score_str} \\\\"
    
    table_content += row + "\n"

# 添加闭源模型部分
table_content += "\\midrule\n\\multicolumn{18}{c}{\\textit{Closed-Source Multimodal Models}} \\\\\n\\midrule\n"

# 对闭源模型按得分排序
closed_source_models = [m for m in models if any(closed_name in m.lower() for closed_name in ['gpt', 'gemini', 'claude', 'doubao'])]
closed_source_models.sort(key=lambda m: results[m]['score'], reverse=True)

# 获取闭源模型中得分前三的模型
top3_closed_source = sorted(closed_source_models, key=lambda m: results[m]['score'], reverse=True)[:3]

for model in closed_source_models:
    # 构建模型行
    row = f"{model} & "
    
    # 诊断 (DD)
    diag_acc_str = f"{results[model]['task1_acc']:.4f}"
    diag_f1_str = f"{results[model]['task1_f1']:.4f}"
    row += f"{diag_acc_str} & {diag_f1_str} & "
    
    # 视图识别 (VRA)
    vra_acc_str = f"{results[model]['task2_acc']:.4f}"
    vra_f1_str = f"{results[model]['task2_f1']:.4f}"
    row += f"{vra_acc_str} & {vra_f1_str} & "
    
    # 病灰定位 (LL)
    ll_acc_str = f"{results[model]['task3_acc']:.4f}"
    row += f"{ll_acc_str} & "
    
    # 目标检测 (OD)
    od_acc_str = f"{results[model]['task4_acc']:.4f}"
    row += f"{od_acc_str} & "
    
    # 关键点检测 (KD)
    kd_acc_str = f"{results[model]['task5_acc']:.4f}"
    row += f"{kd_acc_str} & "
    
    # 连续值估计 (CVE)
    cve_rmse_str = f"{results[model]['task6_rmse']:.4f}"
    cve_std_str = f"{results[model]['task6_std']:.4f}"
    cve_tol_str = f"{results[model]['task6_tol']:.4f}"
    row += f"{cve_rmse_str} & {cve_std_str} & {cve_tol_str} & "
    
    # 报告生成 (RG)
    rg_bleu_str = f"{results[model]['task7_bleu']:.4f}"
    rg_rouge_str = f"{results[model]['task7_rouge']:.4f}"
    rg_bert_str = f"{results[model]['task7_bert']:.4f}"
    row += f"{rg_bleu_str} & {rg_rouge_str} & {rg_bert_str} & "
    
    # 标题生成 (CG)
    cg_bleu_str = f"{results[model]['task8_bleu']:.4f}"
    cg_rouge_str = f"{results[model]['task8_rouge']:.4f}"
    cg_bert_str = f"{results[model]['task8_bert']:.4f}"
    row += f"{cg_bleu_str} & {cg_rouge_str} & {cg_bert_str} & "
    
    # 得分
    score_str = f"{results[model]['score']:.4f}"
    row += f"{score_str} \\\\"
    
    table_content += row + "\n"

# 添加表格底部
table_content += "\\bottomrule\n"

# 保存表格内容到文件
with open('/home/guohongcheng/table_fill/new_table_content_score_format0522.tex', 'w') as f:
    f.write(table_content)

print(f"表格已保存到: /home/guohongcheng/table_fill/new_table_content_score_format0522.tex")
