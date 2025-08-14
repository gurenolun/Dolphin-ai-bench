#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import csv
import random
import base64
from collections import defaultdict
import glob
import re
from datetime import datetime

# 预定义的TSV路径映射
TSV_PATH = {
    '03': '/media/ps/data-ssd/json_processing/ale_tsv_output/03.tsv',  # 分类任务
    '31': '/media/ps/data-ssd/json_processing/ale_tsv_output/31.tsv',  # 分割任务
    '48': '/media/ps/data-ssd/json_processing/ale_tsv_output/single_keypoint/48.tsv'  # 分割任务
}

# 任务描述映射
TASK_DESCRIPTIONS = {
    '03': 'Ultrasound Image Classification',
    '31': 'Thyroid Nodule Segmentation in Ultrasound Images', 
    '48': 'Location Identification in Ultrasound Images'
}

# 模型输出目录
MODEL_OUTPUT_DIR = '/media/ps/data-ssd/benchmark/VLMEvalKit/outputs/dolphin-output'

def extract_coordinates(keypoints_str):
    """从字符串中提取坐标"""
    try:
        fixed_str = keypoints_str.replace("'", '"')
        data = json.loads(fixed_str)
        if isinstance(data, dict):
            return list(data.values())[0]
        else:
            return list(data[0].values())[0]
    except:
        return 'nan'

def get_bounding_box_location(gt_bbox):
    """确定边界框的位置类别"""
    import math
    if isinstance(gt_bbox, str) and gt_bbox == 'nan':
        return 'not visible'
    
    if not isinstance(gt_bbox, (list, tuple)) or len(gt_bbox) < 2:
        return 'not visible'

    try:
        center_x, center_y = float(gt_bbox[0]), float(gt_bbox[1])
    except (ValueError, TypeError):
        return 'not visible'

    if math.isnan(center_x) or math.isnan(center_y):
        return 'not visible'

    LOW_THRESHOLD = 0.45
    HIGH_THRESHOLD = 0.55

    if center_y < LOW_THRESHOLD:
        y_pos = "upper"
    elif center_y < HIGH_THRESHOLD: 
        y_pos = "middle"
    else: 
        y_pos = "lower"

    if center_x < LOW_THRESHOLD:
        x_pos = "left"
    elif center_x < HIGH_THRESHOLD: 
        x_pos = "center"
    else: 
        x_pos = "right"

    if y_pos == "middle" and x_pos == "center":
        return "center"
    else:
        return f"{y_pos} {x_pos}"

def try_load_image(image_path):
    """尝试加载图像并转换为base64"""
    try:
        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return f"data:image/jpeg;base64,{encoded_string}"
        return None
    except Exception as e:
        print(f"Error loading image {image_path}: {str(e)}")
        return None

def read_tsv_data(task_id):
    """读取TSV文件中的标注数据"""
    try:
        tsv_path = TSV_PATH[task_id]
        
        # 使用csv.DictReader读取TSV文件
        data = []
        with open(tsv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                data.append(row)
        
        # 处理不同格式的TSV文件
        for row in data:
            if 'keypoints' in row:
                row['seg_ans'] = extract_coordinates(row['keypoints'])
            elif 'gt_bbox' in row:
                row['seg_ans'] = extract_coordinates(row['gt_bbox'])
                
            # 添加位置标签（仅对任务48适用）
            if task_id == '48' and 'seg_ans' in row:
                row['location'] = get_bounding_box_location(row['seg_ans'])
        
        return data
    except Exception as e:
        print(f"Error reading TSV file for task {task_id}: {str(e)}")
        return None

def find_model_jsonl_file(task_id, model_name):
    """查找模型的JSONL文件"""
    # 根据任务类型确定子目录
    if task_id == '03':
        task_subdir = 'cla'
    elif task_id in ['31', '48']:
        task_subdir = 'seg'
    else:
        task_subdir = 'seg'  # 默认
        
    model_dir = os.path.join(MODEL_OUTPUT_DIR, task_subdir, task_id, model_name)
    if not os.path.isdir(model_dir):
        return None
    
    # 查找JSONL文件
    jsonl_files = glob.glob(os.path.join(model_dir, "*.jsonl"))
    if not jsonl_files:
        return None
    
    # 使用最新的JSONL文件
    return sorted(jsonl_files)[-1]

def read_model_response(task_id, model_name, index):
    """读取模型的响应"""
    try:
        jsonl_path = find_model_jsonl_file(task_id, model_name)
        if not jsonl_path:
            print(f"No JSONL file found for {model_name} on task {task_id}")
            return None, None
            
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if index < len(lines):
                data = json.loads(lines[index])
                return data.get('response', ''), data.get('prompt', '')
            return None, None
    except Exception as e:
        print(f"Error reading model response for {model_name} on task {task_id}: {str(e)}")
        return None, None

def generate_three_case_comparison():
    """生成三案例对比报告"""
    report = []
    report.append("# DolphinV1.6模型三案例对比\n")
    
    # 预定义的三个案例
    cases = [
        {
            'task_id': '48',
            'index': 47,  # 任务48的第48个样本 (0-based index)
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
    
    # 目标模型 - 标准模式和深度推理模式
    target_models = {
        'standard': 'DolphinV1.6r',  # 标准模式
        'deep_reasoning': 'DolphinV1.6rd'  # 深度推理模式
    }
    
    for case_idx, case in enumerate(cases):
        task_id = case['task_id']
        index = case['index']
        title = case['title']
        
        report.append(f"## {title}\n")
        
        # 读取标准答案数据
        gt_data = read_tsv_data(task_id)
        if gt_data is None:
            report.append(f"无法读取任务 {task_id} 的标准答案数据\n")
            continue
            
        if index >= len(gt_data):
            report.append(f"索引 {index} 超出数据范围\n")
            continue
        
        gt_row = gt_data[index]
        
        # 添加图像
        image_path = None
        if 'image_path' in gt_row:
            image_path = gt_row['image_path']
            
        report.append("**图像**:\n")
        
        # 尝试加载图像
        image_data = try_load_image(image_path)
        if image_data:
            report.append(f"![案例{case_idx+1}图像]({image_data})\n")
        else:
            report.append(f"![案例{case_idx+1}图像](图像路径: {image_path})\n")
        
        # 获取两种模式的模型响应
        for mode_name, model_name in target_models.items():
            mode_title = "标准模型" if mode_name == 'standard' else "深度推理模型"
            
            response, prompt = read_model_response(task_id, model_name, index)
            
            if response is not None:
                report.append(f"**{mode_title}回答**:")
                report.append("```")
                response_clean = response.strip()
                # 对于深度推理模式，提取</think>后的内容
                if mode_name == 'deep_reasoning' and '</think>' in response_clean:
                    response_clean = response_clean.split('</think>')[-1].strip()
                report.append(response_clean)
                report.append("```\n")
            else:
                report.append(f"**{mode_title}回答**:")
                report.append("```")
                report.append("无法获取模型响应")
                report.append("```\n")
        
        # 添加参考答案
        if task_id == '48':
            # 位置识别任务
            gt_location = gt_row.get('location', 'unknown')
            report.append("**参考答案**:")
            report.append("```")
            report.append(gt_location)
            report.append("```\n")
        elif task_id == '03':
            # 分类任务
            if 'answer' in gt_row:
                report.append("**参考答案**:")
                report.append("```")
                report.append(str(gt_row['answer']))
                report.append("```\n")
        else:
            # 其他分割任务
            if 'seg_ans' in gt_row:
                report.append("**参考答案**:")
                report.append("```")
                report.append(str(gt_row['seg_ans']))
                report.append("```\n")
        
        report.append("---\n")
    
    return "\n".join(report)

def main():
    """主函数"""
    try:
        print("开始生成三案例对比报告...")
        report = generate_three_case_comparison()
        
        # 保存报告到当前目录
        output_file = "DolphinV1.6_三案例对比报告.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"三案例对比报告已生成: {output_file}")
        
        # 同时保存到reports目录
        reports_dir = "../reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
            
        reports_output = os.path.join(reports_dir, output_file)
        with open(reports_output, 'w', encoding='utf-8') as f:
            f.write(report)
            
        print(f"报告也已保存到: {reports_output}")
        
    except Exception as e:
        print(f"生成报告时出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 