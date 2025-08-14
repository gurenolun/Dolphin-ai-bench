#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import random
import glob
import base64
import ast
import math
from collections import defaultdict
import re
import pandas as pd
import numpy as np
import io
from PIL import Image

# 基础目录
BASE_DIR = '/home/guohongcheng/Dolphin0606_processed_results_final'
# 图像基础路径
IMAGE_BASE_DIR = '/media/ps/data-ssd/benchmark/VLMEvalKit/data'
# 输出报告路径
OUTPUT_FILE = '/home/guohongcheng/dolphin_examples_report_improved.md'

# TSV文件路径映射，使用嵌套结构避免重复
TSV_PATH = {
    'cla': {
        '03': '/media/ps/data-ssd/json_processing/ale_tsv_output/classification_tsv_output/3_FETAL_Planes_US.tsv',
        '10': '/media/ps/data-ssd/json_processing/ale_tsv_output/classification_tsv_output/10_FetusOrientation.tsv',
        '18': '/media/ps/data-ssd/json_processing/ale_tsv_output/classification_tsv_output/18_1.Ultrasound_Heart_Segmentation_Dataset_view.tsv',
        '21': '/media/ps/data-ssd/json_processing/ale_tsv_output/21.Breast_Ultrasound_Segmentation_Dataset.tsv',
        '23': '/media/ps/data-ssd/json_processing/ale_tsv_output/23.tsv',
        '25': '/media/ps/data-ssd/json_processing/ale_tsv_output/25.Dermatologic_Ultrasound_Classification_Dataset.tsv',
        '28': '/media/ps/data-ssd/json_processing/ale_tsv_output/classification_tsv_output/28_1.Knee_Grading_Ultrasound_Classification_Dataset_Kellgren-Lawrence (KL) Grade.tsv',
        '28_class': '/media/ps/data-ssd/json_processing/ale_tsv_output/28.Knee_Classification.tsv',
        '32': '/media/ps/data-ssd/json_processing/ale_tsv_output/32_image.tsv',
        '37': '/media/ps/data-ssd/json_processing/ale_tsv_output/37.tsv',
        '40': '/media/ps/data-ssd/json_processing/ale_tsv_output/classification_tsv_output/40_birads.tsv',
        '42': '/media/ps/data-ssd/json_processing/ale_tsv_output/42.tsv',
        '44': '/media/ps/data-ssd/json_processing/ale_tsv_output/44.COVID-BLUES-frames.tsv',
        '50': '/media/ps/data-ssd/json_processing/ale_tsv_output/classification_tsv_output/50.ACOUSLIC_AI_Key_Frame_Classification_is_optimal_or_suboptimal.tsv',
        '53': '/media/ps/data-ssd/json_processing/ale_tsv_output/53.tsv',
        '57': '/media/ps/data-ssd/json_processing/ale_tsv_output/57_1.Liver_Ultrasound_Segmentation_Dataset.tsv',
        '66': '/media/ps/data-ssd/json_processing/ale_tsv_output/66.tsv',
        '69': '/media/ps/data-ssd/json_processing/ale_tsv_output/classification_tsv_output/69.tsv',
        '70': '/media/ps/data-ssd/json_processing/ale_tsv_output/70.tsv',
        '74is_normal': '/media/ps/data-ssd/json_processing/ale_tsv_output/classification_tsv_output/74_is_normal.tsv',
        '74is_visible': '/media/ps/data-ssd/json_processing/ale_tsv_output/classification_tsv_output/74_is_visible.tsv',
        '75': '/media/ps/data-ssd/json_processing/ale_tsv_output/75.PCOS_Ultrasound_Classification_Dataset.tsv',
        'anatomy': '/media/ps/data-ssd/json_processing/ale_tsv_output/classification_tsv_output/anatomy.tsv',
    },
    'seg': {
        '04': '/media/ps/data-ssd/json_processing/ale_tsv_output/04.tsv',
        '09': '/media/ps/data-ssd/json_processing/ale_tsv_output/single_channel_seg/09.tsv',
        '13': '/media/ps/data-ssd/json_processing/ale_tsv_output/single_channel_seg/13.tsv',
        '16': '/media/ps/data-ssd/json_processing/ale_tsv_output/single_channel_seg/16.tsv',
        '17': '/media/ps/data-ssd/json_processing/ale_tsv_output/17_1.tsv',
        '18': '/media/ps/data-ssd/json_processing/ale_tsv_output/single_channel_seg/18_1.Ultrasound_Heart_Segmentation_Dataset.tsv',
        '23': '/media/ps/data-ssd/json_processing/ale_tsv_output/23.tsv',
        '31': '/media/ps/data-ssd/json_processing/ale_tsv_output/31.tsv',
        '32': '/media/ps/data-ssd/json_processing/ale_tsv_output/32_image.tsv',
        '37': '/media/ps/data-ssd/json_processing/ale_tsv_output/single_channel_seg/37.tsv',
        '38': '/media/ps/data-ssd/json_processing/ale_tsv_output/38.tsv',
        '47': '/media/ps/data-ssd/json_processing/ale_tsv_output/47.tsv',
        '48': '/media/ps/data-ssd/json_processing/ale_tsv_output/single_keypoint/48.tsv',
        '49': '/media/ps/data-ssd/json_processing/ale_tsv_output/49.tsv',
        '50': '/media/ps/data-ssd/json_processing/ale_tsv_output/50.tsv',
        '52': '/media/ps/data-ssd/json_processing/ale_tsv_output/single_channel_seg/52.tsv',
        '53': '/media/ps/data-ssd/json_processing/ale_tsv_output/single_channel_seg/53.tsv',
        '64': '/media/ps/data-ssd/json_processing/ale_tsv_output/64.BrEaST-Lesions_USG-images_and_masks-Dec-15-2023.tsv',
        '67': '/media/ps/data-ssd/json_processing/ale_tsv_output/single_channel_seg/67.tsv',
    },
    'measurement': {
        '18': '/media/ps/data-ssd/json_processing/ale_tsv_output/18_1.Ultrasound_Heart_Segmentation_Dataset.tsv',
        '27': '/media/ps/data-ssd/json_processing/ale_tsv_output/27.tsv',
        '31': '/media/ps/data-ssd/json_processing/ale_tsv_output/31.tsv',
        '50': '/media/ps/data-ssd/json_processing/ale_tsv_output/50.tsv',
        '57': '/media/ps/data-ssd/json_processing/ale_tsv_output/57_1.Liver_Ultrasound_Segmentation_Dataset.tsv',
    },
    'measurement_processed_fixed': {
        '18': '/media/ps/data-ssd/json_processing/ale_tsv_output/18_1.Ultrasound_Heart_Segmentation_Dataset.tsv',
        '27': '/media/ps/data-ssd/json_processing/ale_tsv_output/27.tsv',
        '31': '/media/ps/data-ssd/json_processing/ale_tsv_output/31.tsv',
        '50': '/media/ps/data-ssd/json_processing/ale_tsv_output/50.tsv',
        '57': '/media/ps/data-ssd/json_processing/ale_tsv_output/57_1.Liver_Ultrasound_Segmentation_Dataset.tsv',
    },
    'report': {
        '10': '/media/ps/data-ssd/json_processing/ale_tsv_output/10.tsv',
        '11': '/media/ps/data-ssd/json_processing/ale_tsv_output/11.Thyroid_US_Images.tsv',
        '39': '/media/ps/data-ssd/json_processing/ale_tsv_output/39_translated.tsv',
        '44': '/media/ps/data-ssd/json_processing/ale_tsv_output/44.COVID-BLUES-frames.tsv',
    }
}

# 任务类型映射（英文）
TASK_TYPES = {
    'cla': 'Classification Task',
    'seg': 'Segmentation Task',
    'measurement_processed_fixed': 'Measurement Task',
    'report': 'Report Generation Task'
}

# 任务描述映射（英文）
TASK_DESCRIPTIONS = {
    # 分类任务
    'cla/03': 'Ultrasound Image Anatomy Classification',
    'cla/10': 'Fetus Orientation Classification',
    'cla/18': 'Heart View Classification',
    'cla/21': 'Breast Ultrasound Classification',
    'cla/23': 'Ultrasound Classification',
    'cla/25': 'Dermatologic Ultrasound Classification',
    'cla/28_class': 'Knee Classification',
    'cla/32': 'Ultrasound Classification',
    'cla/37': 'Ultrasound Classification',
    'cla/40': 'BI-RADS Classification',
    'cla/42': 'Ultrasound Classification',
    'cla/44': 'COVID-19 Classification',
    'cla/50': 'Acoustic Key Frame Classification',
    'cla/53': 'Ultrasound Classification',
    'cla/57': 'Liver Ultrasound Classification',
    'cla/66': 'Ultrasound Classification',
    'cla/69': 'Ultrasound Classification',
    'cla/70': 'Ultrasound Classification',
    'cla/74is_normal': 'Normal Ultrasound Classification',
    'cla/74is_visible': 'Visibility Classification',
    'cla/75': 'PCOS Ultrasound Classification',
    'cla/anatomy': 'Anatomy Classification',
    
    # 分割任务
    'seg/04': 'Liver Segmentation',
    'seg/09': 'Fetal Head Segmentation',
    'seg/13': 'Kidney Segmentation',
    'seg/16': 'Bladder Segmentation',
    'seg/17': 'Fetal Head Segmentation',
    'seg/48': 'Position Recognition',
    
    # 测量任务
    'measurement_processed_fixed/18': 'Heart Measurement',
    'measurement_processed_fixed/27': 'Fetal Measurement',
    'measurement_processed_fixed/31': 'Thyroid Measurement',
    'measurement_processed_fixed/50': 'Thyroid Nodule Measurement',
    'measurement_processed_fixed/57': 'Liver Measurement',
    
    # 报告生成任务
    'report/10': 'Ultrasound Report Generation',
    'report/11': 'Ultrasound Report Generation',
    'report/44': 'COVID-19 Report Generation'
}

def try_load_image(image_path):
    """尝试加载图像并转换为base64"""
    try:
        # 检查是否是列表格式的路径
        if isinstance(image_path, str) and image_path.startswith('['):
            try:
                # 安全地解析为列表
                path_list = ast.literal_eval(image_path)
                if isinstance(path_list, list) and len(path_list) > 0:
                    image_path = path_list[0]  # 使用第一个路径
            except (ValueError, SyntaxError) as e:
                print(f"解析路径列表失败: {e}")
                pass
        
        # 构建完整路径
        if image_path and not image_path.startswith('/'):
            full_path = os.path.join(IMAGE_BASE_DIR, image_path)
        else:
            full_path = image_path
            
        if full_path and os.path.exists(full_path):
            with open(full_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return f"data:image/png;base64,{encoded_string}"
        else:
            print(f"图像文件不存在: {full_path}")
            
            # 尝试在其他可能的位置查找图像
            alternative_paths = [
                os.path.join('/home/guohongcheng/ultrasound_datasets', image_path),
                os.path.join('/media/ps/data-ssd/benchmark/VLMEvalKit', image_path),
                os.path.join('/media/ps/data-ssd/json_processing', image_path)
            ]
            
            for alt_path in alternative_paths:
                if os.path.exists(alt_path):
                    print(f"找到替代路径: {alt_path}")
                    with open(alt_path, "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                        return f"data:image/png;base64,{encoded_string}"
                    
        return None
    except Exception as e:
        print(f"加载图像 {image_path} 出错: {str(e)}")
        return None

def extract_image_path_from_question(question):
    """从问题中提取图像路径"""
    # 尝试从问题中提取图像路径
    img_path = None
    
    for item in question:
        if item.get('type') == 'image':
            img_path = item.get('value', '')
            break
    
    return img_path

def extract_options_from_question(question):
    """从问题中提取选项"""
    options = []
    
    for item in question:
        if item.get('type') == 'text':
            text = item.get('value', '')
            if 'options:' in text.lower():
                # 尝试提取引号中的选项
                quoted_options = re.findall(r"['\"]([^'\"]*?)['\"]", text)
                if quoted_options:
                    options = quoted_options
                    break
                    
                # 如果没有找到引号中的选项，尝试提取冒号后的部分
                if not options:
                    parts = text.lower().split('options:')
                    if len(parts) > 1:
                        # 尝试按逗号分割
                        comma_options = parts[1].strip().split(',')
                        options = [opt.strip() for opt in comma_options if opt.strip()]
    
    return options

def get_bounding_box_location_v1(gt_bbox):
    """
    将边界框坐标转换为位置描述（来自qwen_seg_eval.py）
    """
    if isinstance(gt_bbox, float) and math.isnan(gt_bbox):  # For gt_bbox = float('nan')
        return 'not visible'
    
    # Check if gt_bbox is a sequence of expected length
    if not isinstance(gt_bbox, (list, tuple)) or len(gt_bbox) < 2:  # Expecting at least center_x, center_y
        return 'not visible'

    try:
        center_x, center_y = float(gt_bbox[0]), float(gt_bbox[1])
    except (ValueError, TypeError):  # Handles non-numeric values in gt_bbox
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

def read_tsv_reference(task_type, task_id):
    """根据任务类型从TSV文件中读取参考答案"""
    tsv_file = None
    
    # 首先检查任务类型是否存在
    if task_type in TSV_PATH:
        task_dict = TSV_PATH[task_type]
        
        # 尝试不同的键格式
        tsv_keys = [
            task_id,
            f"{task_id}_class" if task_type == 'cla' else task_id,
            f"{task_id}is_normal" if task_type == 'cla' else None,
            f"{task_id}is_visible" if task_type == 'cla' else None,
        ]
        
        # 过滤掉None值
        tsv_keys = [key for key in tsv_keys if key is not None]
        
        for key in tsv_keys:
            if key in task_dict:
                tsv_file = task_dict[key]
                break
    
    if not tsv_file:
        print(f"未找到任务 {task_type}/{task_id} 的TSV文件")
        return None
    
    try:
        df_tsv = pd.read_csv(tsv_file, sep='\t')
        
        # 根据任务类型进行不同的处理
        if task_type == 'cla':
            # 分类任务的特殊处理
            if task_id == 'anatomy':
                # 处理anatomy任务
                try:
                    classes_data = []
                    for _, row in df_tsv.iterrows():
                        if 'classes' in df_tsv.columns:
                            classes_value = row['classes']
                            if isinstance(classes_value, str):
                                # 尝试解析JSON字符串
                                try:
                                    classes_dict = json.loads(classes_value.replace("'", '"'))
                                    if isinstance(classes_dict, dict) and 'Anatomy' in classes_dict:
                                        classes_data.append(classes_dict['Anatomy'])
                                    else:
                                        classes_data.append(classes_value)
                                except json.JSONDecodeError:
                                    # 如果解析失败，尝试使用正则表达式提取
                                    match = re.search(r'"Anatomy":\s*"([^"]+)"', classes_value)
                                    if match:
                                        classes_data.append(match.group(1))
                                    else:
                                        classes_data.append(classes_value)
                            else:
                                classes_data.append(str(classes_value))
                        else:
                            classes_data.append('')
                    
                    # 将提取的Anatomy值赋给df_tsv
                    df_tsv['reference_answer'] = classes_data
                except Exception as e:
                    print(f"处理anatomy任务时出错: {e}")
                    # 回退到默认处理方式
                    if 'classes' in df_tsv.columns:
                        df_tsv['reference_answer'] = df_tsv['classes']
                    else:
                        df_tsv['reference_answer'] = df_tsv['class']
            else:
                # 其他分类任务
                if 'classes' in df_tsv.columns:
                    df_tsv['reference_answer'] = df_tsv['classes']
                elif 'class' in df_tsv.columns:
                    df_tsv['reference_answer'] = df_tsv['class']
                else:
                    print(f"警告：TSV文件中没有找到classes或class列")
                    
        elif task_type == 'seg':
            # 分割任务的处理
            def extract_coordinates_and_convert_to_location(keypoints_str):
                try:
                    # 首先提取坐标
                    if isinstance(keypoints_str, str):
                        fixed_str = keypoints_str.replace("'", '"')
                        data = json.loads(fixed_str)
                        if isinstance(data, dict):
                            coordinates = list(data.values())[0]  # 这种情况下，默认只有一对坐标需要提取
                        else:
                            coordinates = list(data[0].values())[0]  # 只取第一个
                    else:
                        coordinates = keypoints_str
                    
                    # 然后转换为位置描述
                    location = get_bounding_box_location_v1(coordinates)
                    return location
                    
                except (json.JSONDecodeError, ValueError, KeyError, IndexError) as e:
                    print(f"提取坐标时出错: {e}")
                    return 'not visible'
            
            if 'keypoints' in df_tsv.columns:
                df_tsv['reference_answer'] = df_tsv['keypoints'].apply(extract_coordinates_and_convert_to_location)
            elif 'gt_bbox' in df_tsv.columns:
                df_tsv['reference_answer'] = df_tsv['gt_bbox'].apply(extract_coordinates_and_convert_to_location)
            elif 'seg_ans' in df_tsv.columns:
                # seg_ans列可能已经是坐标，直接转换为位置
                df_tsv['reference_answer'] = df_tsv['seg_ans'].apply(lambda x: get_bounding_box_location_v1(x))
            else:
                print(f"警告：TSV文件中没有找到分割相关的列")
                
        elif task_type in ['measurement', 'measurement_processed_fixed']:
            # 测量任务的处理
            def extract_mea(measurements_str):
                try:
                    if isinstance(measurements_str, str):
                        fixed_str = measurements_str.replace("'", '"')
                        data = json.loads(fixed_str)
                        if isinstance(data, dict):
                            if task_id == '18':
                                return data.get('EF', data)
                            elif task_id == '27':
                                return list(data.get('IMT', data))[0] if 'IMT' in data else data
                            elif task_id == '31':
                                return data
                            elif task_id == '50':
                                return data.get('abdominal_circumference', data)
                            else:
                                return data.get('fat value', data)
                        elif isinstance(data, list):
                            return list(data[0].values())[0]
                    return str(measurements_str)
                except (json.JSONDecodeError, ValueError, KeyError, IndexError, TypeError) as e:
                    print(f"提取测量值时出错: {e}")
                    return str(measurements_str)
            
            if 'measurement' in df_tsv.columns:
                df_tsv['reference_answer'] = df_tsv['measurement'].apply(extract_mea)
            elif 'measurement_ans' in df_tsv.columns:
                df_tsv['reference_answer'] = df_tsv['measurement_ans']
            else:
                print(f"警告：TSV文件中没有找到测量相关的列")
                
        elif task_type == 'report':
            # 报告任务的处理
            if 'caption' in df_tsv.columns:
                df_tsv['reference_answer'] = df_tsv['caption']
            else:
                print(f"警告：TSV文件中没有找到caption列")
        
        return df_tsv
    except Exception as e:
        print(f"读取TSV文件出错: {str(e)}")
        return None

def extract_ground_truth_from_jsonl(jsonl_file):
    """从JSONL文件中提取问题数据"""
    gt_data = []
    
    try:
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    gt_data.append({
                        'id': data.get('id', ''),
                        'question': data.get('question', []),
                        'img_path': extract_image_path_from_question(data.get('question', [])),
                        'options': extract_options_from_question(data.get('question', []))
                    })
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"读取JSONL文件出错: {str(e)}")
    
    return gt_data

def find_model_response_file(task_path):
    """查找模型响应文件"""
    # 参考其他评估脚本的路径结构
    task_type, task_id = task_path.split('/')
    task_dir = os.path.join(BASE_DIR, task_type, task_id)
    
    if not os.path.exists(task_dir):
        return None
    
    # 遍历所有模型目录
    for model_name in os.listdir(task_dir):
        model_dir = os.path.join(task_dir, model_name)
        if os.path.isdir(model_dir) and ('Dolphon' in model_name or 'Dolphin' in model_name):
            # 查找JSONL文件
            jsonl_files = [f for f in os.listdir(model_dir) if f.endswith('.jsonl')]
            if jsonl_files:
                # 按时间排序，使用最新的文件
                jsonl_files.sort()
                return os.path.join(model_dir, jsonl_files[-1])
    
    return None

def extract_examples_for_task(task_type, task_id, num_examples=2):
    """为指定任务提取示例"""
    task_path = f"{task_type}/{task_id}"
    full_task_path = os.path.join(BASE_DIR, task_path)
    
    # 查找模型响应文件
    model_response_file = find_model_response_file(task_path)
    if not model_response_file:
        print(f"未找到任务 {task_path} 的模型响应文件")
        return []
    
    # 提取问题数据
    gt_data = extract_ground_truth_from_jsonl(model_response_file)
    if not gt_data:
        print(f"任务 {task_path} 没有有效的问题数据")
        return []
    
    # 读取TSV参考答案
    df_tsv = read_tsv_reference(task_type, task_id)
    
    # 读取模型响应
    model_responses = []
    try:
        with open(model_response_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    # 从question字段中提取prompt文本
                    prompt_text = ''
                    question = data.get('question', [])
                    if isinstance(question, list):
                        for item in question:
                            if item.get('type') == 'text':
                                prompt_text = item.get('value', '')
                                break
                    
                    model_responses.append({
                        'id': data.get('id', ''),
                        'response': data.get('response', data.get('original_response', '')),
                        'prompt': prompt_text or data.get('prompt', '')
                    })
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"读取模型响应文件出错: {str(e)}")
        return []
    
    # 将模型响应转换为字典以便快速查找
    resp_dict = {resp['id']: resp for resp in model_responses}
    
    # 合并数据
    examples = []
    for gt in gt_data:
        if gt['id'] in resp_dict:
            resp = resp_dict[gt['id']]
            
            # 从TSV中获取参考答案
            reference_answer = ""
            if df_tsv is not None:
                try:
                    # 尝试按ID匹配
                    if 'id' in df_tsv.columns:
                        row = df_tsv[df_tsv['id'] == gt['id']]
                        if not row.empty and 'reference_answer' in df_tsv.columns:
                            reference_answer = row['reference_answer'].values[0]
                    
                    # 如果没有匹配到，使用相同索引的行
                    if not reference_answer:
                        idx = gt_data.index(gt)
                        if idx < len(df_tsv) and 'reference_answer' in df_tsv.columns:
                            reference_answer = df_tsv['reference_answer'].iloc[idx]
                except Exception as e:
                    print(f"从TSV获取参考答案出错: {str(e)}")
            
            examples.append({
                'id': gt['id'],
                'question': gt['question'],
                'img_path': gt['img_path'],
                'options': gt['options'],
                'answer': reference_answer,
                'response': resp['response'],
                'prompt': resp['prompt']
            })
    
    # 根据任务类型选择示例
    selected_examples = []
    
    if task_type == 'cla':
        # 分类任务：选择回复完全正确的示例
        correct_examples = []
        for ex in examples:
            if ex['answer'] and isinstance(ex['answer'], str) and isinstance(ex['response'], str) and ex['answer'].lower() in ex['response'].lower():
                correct_examples.append(ex)
        
        # 如果正确示例不足，则随机选择
        if len(correct_examples) >= num_examples:
            selected_examples = random.sample(correct_examples, num_examples)
        else:
            selected_examples = correct_examples
            remaining = num_examples - len(correct_examples)
            if remaining > 0 and len(examples) > len(correct_examples):
                remaining_examples = [ex for ex in examples if ex not in correct_examples]
                selected_examples.extend(random.sample(remaining_examples, min(remaining, len(remaining_examples))))
    
    elif task_type == 'seg':
        # 分割任务：选择回复完全正确的示例
        correct_examples = []
        for ex in examples:
            if ex['answer'] and isinstance(ex['answer'], str) and isinstance(ex['response'], str) and ex['answer'].lower() in ex['response'].lower():
                correct_examples.append(ex)
        
        # 如果正确示例不足，则随机选择
        if len(correct_examples) >= num_examples:
            selected_examples = random.sample(correct_examples, num_examples)
        else:
            selected_examples = correct_examples
            remaining = num_examples - len(correct_examples)
            if remaining > 0 and len(examples) > len(correct_examples):
                remaining_examples = [ex for ex in examples if ex not in correct_examples]
                selected_examples.extend(random.sample(remaining_examples, min(remaining, len(remaining_examples))))
    
    elif task_type == 'measurement_processed_fixed':
        # 测量任务：选择尽可能相似的示例
        # 这里简单实现，实际上可以使用更复杂的相似度计算
        selected_examples = random.sample(examples, min(num_examples, len(examples)))
    
    else:  # report
        # 报告生成任务：随机选择
        selected_examples = random.sample(examples, min(num_examples, len(examples)))
    
    return selected_examples

def generate_report(examples_by_task):
    """生成报告"""
    report = []
    report.append("# Dolphin Model Response Examples Report\n")
    
    for task_key, examples in examples_by_task.items():
        task_type, task_id = task_key.split('/')
        task_description = TASK_DESCRIPTIONS.get(task_key, f"{TASK_TYPES.get(task_type, 'Unknown Task')} {task_id}")
        
        report.append(f"## {task_description} (Task ID: {task_id})\n")
        
        for i, example in enumerate(examples):
            report.append(f"### Example {i+1}\n")
            
            # 图像
            if example['img_path']:
                report.append(f"**Image Path**: {example['img_path']}")
                image_data = try_load_image(example['img_path'])
                if image_data:
                    report.append(f"\n![Image {i+1}]({image_data})\n")
            
            # 提示（保留英文原文）
            report.append("**Prompt**:")
            report.append("```")
            if example['prompt']:
                report.append(example['prompt'])
            else:
                # 根据任务类型生成默认提示（英文）
                if task_type == 'cla':
                    options_str = ', '.join(example['options']) if example['options'] else 'No options provided'
                    report.append(f"Please analyze this ultrasound image and select the correct anatomical structure. Options: {options_str}")
                elif task_type == 'seg':
                    report.append("Please analyze this ultrasound image and identify the location or boundaries of the target structure.")
                elif task_type == 'measurement_processed_fixed':
                    report.append("Please analyze this ultrasound image and provide the corresponding measurements.")
                else:  # report
                    report.append("Please generate a diagnostic report based on this ultrasound image.")
            report.append("```\n")
            
            # 模型回复
            report.append("**Model Response**:")
            report.append("```")
            report.append(str(example['response']))
            report.append("```\n")
            
            # 参考答案
            report.append("**Reference Answer**:")
            report.append("```")
            report.append(str(example['answer']))
            report.append("```\n")
    
    return "\n".join(report)

def scan_available_tasks():
    """扫描所有可用的任务"""
    available_tasks = []
    
    # 参考其他评估脚本的路径结构
    # 直接扫描每种任务类型的目录
    task_types = ['cla', 'seg', 'measurement', 'measurement_processed_fixed', 'report']
    
    for task_type in task_types:
        task_type_dir = os.path.join(BASE_DIR, task_type)
        if not os.path.exists(task_type_dir):
            continue
            
        # 扫描任务类型目录下的所有任务ID目录
        for task_id in os.listdir(task_type_dir):
            task_id_path = os.path.join(task_type_dir, task_id)
            if os.path.isdir(task_id_path):
                # 检查是否有模型响应文件
                model_response_file = find_model_response_file(f"{task_type}/{task_id}")
                if model_response_file:
                    available_tasks.append((task_type, task_id))
    
    return available_tasks

def main():
    # 扫描所有可用的任务
    available_tasks = scan_available_tasks()
    print(f"找到 {len(available_tasks)} 个可用任务")
    
    # 提取示例
    examples_by_task = {}
    for task_type, task_id in available_tasks:
        print(f"处理任务: {task_type}/{task_id}")
        examples = extract_examples_for_task(task_type, task_id, num_examples=3)
        if examples:
            examples_by_task[f"{task_type}/{task_id}"] = examples
    
    # 生成报告
    report = generate_report(examples_by_task)
    
    # 保存报告
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"报告已保存至 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
