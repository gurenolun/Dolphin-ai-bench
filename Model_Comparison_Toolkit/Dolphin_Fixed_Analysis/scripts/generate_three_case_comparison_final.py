#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
import base64
from PIL import Image
import io

# 预定义的TSV路径映射
TSV_PATH = {
    '03': 'data/tsv/classification_tsv_output/3_FETAL_Planes_US.tsv',
    '31': 'data/tsv/31.tsv',
    '48': 'data/tsv/single_keypoint/48.tsv'
}

# 任务描述映射
TASK_DESCRIPTIONS = {
    '03': '胎儿超声图像平面分类',
    '31': '甲状腺结节分割',
    '48': '超声图像位置识别'
}

# 模型输出目录配置
MODEL_CONFIGS = {
    'standard': {
        'name': 'DolphinV1.9p (标准模式)',
        'base_dir': '/path/to/DolphinV1.9p'
    },
    'deep': {
        'name': 'DolphinV1.9 (深度推理模式)', 
        'base_dir': '/path/to/DolphinV1.9'
    }
}

def image_to_base64(image_path):
    """将图片转换为base64格式"""
    try:
        if not os.path.exists(image_path):
            return None
        
        # 打开图片并转换为RGB格式
        with Image.open(image_path) as img:
            # 如果图片太大，调整大小以减少文件大小
            max_size = (800, 600)
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # 转换为RGB格式（确保兼容性）
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 保存到内存中的字节流
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            buffer.seek(0)
            
            # 转换为base64
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            return img_base64
            
    except Exception as e:
        print(f"转换图片失败 {image_path}: {e}")
        return None

def read_jsonl_with_tsv_cla(jsonl_path, tsv_path, task_id):
    """分类任务的数据读取逻辑"""
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        jsonl_data = [json.loads(line.strip()) for line in f]
    df_jsonl = pd.DataFrame(jsonl_data)
    
    df_tsv = pd.read_csv(tsv_path, sep='\t')
    
    # 按行号合并
    if 'classes' in df_tsv.columns:
        df_jsonl['reference_answer'] = df_tsv['classes'].values
    else:
        df_jsonl['reference_answer'] = df_tsv['class'].values
    
    return df_jsonl

def read_jsonl_with_tsv_seg(jsonl_path, tsv_path, task_id):
    """分割任务的数据读取逻辑"""
    def extract_coordinates(keypoints_str):
        try:
            fixed_str = keypoints_str.replace("'", '"')
            data = json.loads(fixed_str)
            if isinstance(data, dict):
                return list(data.values())[0]
            else:
                return list(data[0].values())[0]
        except:
            return 'nan'
    
    with open(jsonl_path, 'r') as f:
        jsonl_data = [json.loads(line) for line in f]
    df_jsonl = pd.DataFrame(jsonl_data)
    
    df_tsv = pd.read_csv(tsv_path, sep='\t')
    
    # 按ID匹配或行号匹配
    if 'id' in df_jsonl.columns and 'id' in df_tsv.columns:
        df_merged = pd.merge(df_jsonl, df_tsv[['id', 'seg_ans']], on='id', how='left')
        df_jsonl['reference_answer'] = df_merged['seg_ans']
    else:
        if 'keypoints' in df_tsv.columns:
            df_jsonl['reference_answer'] = df_tsv['keypoints'].apply(extract_coordinates)
        elif 'gt_bbox' in df_tsv.columns:
            df_jsonl['reference_answer'] = df_tsv['gt_bbox'].apply(extract_coordinates)
    
    return df_jsonl

def get_bounding_box_location(gt_bbox):
    """位置识别的处理逻辑（来自seg_eval）"""
    import math
    if isinstance(gt_bbox, float) and math.isnan(gt_bbox):
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

def find_model_jsonl_file(base_dir, task_id):
    """查找模型输出的JSONL文件"""
    if task_id in ['03']:
        task_dir = os.path.join(base_dir, 'cla', task_id)
    elif task_id in ['31', '48']:
        task_dir = os.path.join(base_dir, 'seg', task_id)
    else:
        return None
    
    if not os.path.exists(task_dir):
        return None
    
    # 查找JSONL文件，支持不同的子目录名
    for root, dirs, files in os.walk(task_dir):
        for file in files:
            if file.endswith('.jsonl'):
                return os.path.join(root, file)
    
    return None

def extract_model_response(response_text, model_type):
    """提取模型回复，处理深度推理模式的</think>标签"""
    if response_text is None:
        return "无回复"
    
    # 清理文本
    cleaned_response = response_text.strip()
    
    # 如果是深度推理模式，提取</think>后的内容
    if model_type == 'deep' and '</think>' in cleaned_response:
        parts = cleaned_response.split('</think>')
        if len(parts) > 1:
            cleaned_response = parts[-1].strip()
    
    return cleaned_response

def generate_three_case_comparison():
    """生成三案例对比报告"""
    
    # 预定义的三个案例
    cases = [
        {
            'task_id': '48',
            'index': 47,  # 任务48的第48个样本（0-based index为47）
            'description': '超声图像位置识别 - 案例48'
        },
        {
            'task_id': '31', 
            'index': 30,  # 任务31的第31个样本（0-based index为30）
            'description': '甲状腺结节分割 - 案例31'
        },
        {
            'task_id': '03',
            'index': 2,   # 任务03的第3个样本（0-based index为2）
            'description': '胎儿超声平面分类 - 案例03'
        }
    ]
    
    report_content = []
    report_content.append("# DolphinV1.9 三案例对比报告")
    report_content.append("")
    report_content.append(f"**生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
    report_content.append("")
    report_content.append("## 概述")
    report_content.append("")
    report_content.append("本报告对比了DolphinV1.9模型在标准模式和深度推理模式下的表现，通过三个具体案例展示两种模式的差异。")
    report_content.append("")
    
    case_count = 0
    
    for case in cases:
        case_count += 1
        task_id = case['task_id']
        index = case['index']
        description = case['description']
        
        report_content.append(f"## 案例 {case_count}: {description}")
        report_content.append("")
        
        # 获取两个模型的数据
        standard_data = None
        deep_data = None
        
        # 读取标准模式数据
        standard_jsonl = find_model_jsonl_file(MODEL_CONFIGS['standard']['base_dir'], task_id)
        if standard_jsonl and os.path.exists(standard_jsonl):
            try:
                if task_id == '03':
                    standard_data = read_jsonl_with_tsv_cla(standard_jsonl, TSV_PATH[task_id], task_id)
                else:
                    standard_data = read_jsonl_with_tsv_seg(standard_jsonl, TSV_PATH[task_id], task_id)
            except Exception as e:
                print(f"读取标准模式数据失败: {e}")
        
        # 读取深度推理模式数据
        deep_jsonl = find_model_jsonl_file(MODEL_CONFIGS['deep']['base_dir'], task_id)
        if deep_jsonl and os.path.exists(deep_jsonl):
            try:
                if task_id == '03':
                    deep_data = read_jsonl_with_tsv_cla(deep_jsonl, TSV_PATH[task_id], task_id)
                else:
                    deep_data = read_jsonl_with_tsv_seg(deep_jsonl, TSV_PATH[task_id], task_id)
            except Exception as e:
                print(f"读取深度推理模式数据失败: {e}")
        
        # 提取指定索引的样本数据
        if standard_data is not None and len(standard_data) > index:
            standard_sample = standard_data.iloc[index]
            # 正确提取图片路径
            images = standard_sample.get('images', [])
            if images and len(images) > 0:
                image_path = images[0]  # 取第一个图片路径
            else:
                image_path = standard_sample.get('image', '未找到图片路径')
            
            reference_answer = standard_sample.get('reference_answer', '未找到参考答案')
            
            # 处理参考答案（特别是位置识别任务）
            if task_id == '48':
                reference_answer = get_bounding_box_location(reference_answer)
            
            standard_response = extract_model_response(
                standard_sample.get('response', ''), 'standard'
            )
        else:
            image_path = "数据不可用"
            reference_answer = "数据不可用"
            standard_response = "数据不可用"
        
        if deep_data is not None and len(deep_data) > index:
            deep_sample = deep_data.iloc[index]
            deep_response = extract_model_response(
                deep_sample.get('response', ''), 'deep'
            )
        else:
            deep_response = "数据不可用"
        
        # 添加案例信息到报告
        report_content.append(f"**任务类型**: {TASK_DESCRIPTIONS.get(task_id, '未知任务')}")
        report_content.append(f"**图片路径**: `{image_path}`")
        
        # 尝试嵌入图片
        if image_path != "数据不可用" and image_path != "未找到图片路径":
            print(f"正在处理图片: {image_path}")
            img_base64 = image_to_base64(image_path)
            if img_base64:
                report_content.append("")
                report_content.append("**图片预览**:")
                report_content.append(f"![案例图片](data:image/jpeg;base64,{img_base64})")
                report_content.append("")
                print(f"✅ 图片已成功嵌入")
            else:
                report_content.append("")
                report_content.append("**图片预览**: 图片加载失败")
                report_content.append("")
                print(f"❌ 图片嵌入失败")
        
        report_content.append(f"**参考答案**: {reference_answer}")
        report_content.append("")
        
        report_content.append("### 模型回复对比")
        report_content.append("")
        
        report_content.append("#### 标准模式 (DolphinV1.9p)")
        report_content.append("```")
        report_content.append(standard_response)
        report_content.append("```")
        report_content.append("")
        
        report_content.append("#### 深度推理模式 (DolphinV1.9)")
        report_content.append("```")
        report_content.append(deep_response)
        report_content.append("```")
        report_content.append("")
        
        # 简单的对比分析
        report_content.append("### 对比分析")
        report_content.append("")
        
        if standard_response != "数据不可用" and deep_response != "数据不可用":
            # 检查答案是否正确
            standard_correct = "✅" if str(reference_answer).lower() in standard_response.lower() else "❌"
            deep_correct = "✅" if str(reference_answer).lower() in deep_response.lower() else "❌"
            
            report_content.append(f"- **标准模式准确性**: {standard_correct}")
            report_content.append(f"- **深度推理模式准确性**: {deep_correct}")
            report_content.append(f"- **回复长度对比**: 标准模式 {len(standard_response)} 字符 vs 深度推理模式 {len(deep_response)} 字符")
        else:
            report_content.append("- 数据不可用，无法进行对比分析")
        
        report_content.append("")
        report_content.append("---")
        report_content.append("")
    
    # 添加总结
    report_content.append("## 总结")
    report_content.append("")
    report_content.append("通过以上三个案例的对比，可以观察到DolphinV1.9模型在标准模式和深度推理模式下的不同表现特点。")
    report_content.append("")
    report_content.append("**报告生成完成**")
    
    # 保存报告
    output_path = "DolphinV1.9_三案例对比报告.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_content))
    
    print(f"✅ 三案例对比报告已生成: {output_path}")
    return output_path

if __name__ == "__main__":
    try:
        report_path = generate_three_case_comparison()
        print(f"报告生成成功，保存在: {report_path}")
    except Exception as e:
        print(f"报告生成失败: {str(e)}")
        import traceback
        traceback.print_exc() 