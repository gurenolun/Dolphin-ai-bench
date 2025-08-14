#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import re
import logging
from pathlib import Path
import argparse

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='/home/guohongcheng/extract_measurement_values_improved.log'
)

def extract_number_from_response(response, task_id):
    """从响应中提取数值，根据任务ID使用不同的提取策略"""
    if not response or response.lower() == 'null':
        return 'null'
    
    # 检查响应是否已经是一个纯数字（整数或浮点数）
    clean_response = response.strip()
    if re.match(r'^\d+\.?\d*$', clean_response):
        return clean_response
    
    # 检查响应中是否包含任何数字
    if not re.search(r'\d', response):
        logging.info(f"响应中不包含数字，返回null (任务ID: {task_id}): '{response}'")
        return 'null'
    
    # 标准化响应文本
    response = response.lower().strip()
    
    # 针对不同任务ID使用不同的提取策略
    if task_id == '57':
        # 针对任务ID 57的特殊处理（肝脏脂肪含量评估）
        patterns = [
            r'around (\d+)',
            r'value of (\d+)',
            r'value around (\d+)',
            r'indicative of (\d+)',
            r'justify a fat value of (\d+)',
            r'fat value (?:of |around |about )?(\d+)',
            r'fat content (?:of |around |about )?(\d+)',
            r'fat percentage (?:of |around |about )?(\d+)',
            r'(\d+)%',  # 百分比格式
            r'(\d+)'    # 最后尝试匹配任何整数
        ]
    elif task_id == '50':
        # 针对任务ID 50的特殊处理（IMT测量）
        patterns = [
            r'imt (?:of |is |value |measurement |measures |approximately |about |around |)(\d+\.?\d*)',
            r'imt (?:of |is |value |measurement |measures |approximately |about |around |)(\d+)',
            r'(\d+\.?\d*)\s*(?:mm|millimeters|millimeter)',
            r'(\d+\.?\d*)',  # 匹配任何数字（整数或浮点数）
            r'(\d+)'         # 匹配任何整数
        ]
    else:
        # 通用处理逻辑，适用于其他任务ID
        patterns = [
            # 带单位的测量值
            r'(\d+\.?\d*)\s*(?:mm|cm|ml|g|kg|%)',
            # 带描述的测量值
            r'(?:value|measurement|result|reading) (?:of |is |approximately |about |around |)(\d+\.?\d*)',
            # 任何浮点数
            r'(\d+\.\d+)',
            # 任何整数
            r'(\d+)'
        ]
    
    # 尝试所有模式匹配
    for pattern in patterns:
        match = re.search(pattern, response)
        if match:
            return match.group(1)
    
    # 如果没有找到数值，记录并返回null
    logging.warning(f"未能提取数值，返回null (任务ID: {task_id}): '{response}'")
    return 'null'

def process_jsonl_file(input_file, output_file, task_id):
    """处理单个JSONL文件，提取数值"""
    processed_entries = 0
    extracted_values = 0
    failed_extractions = 0
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(input_file, 'r', encoding='utf-8') as f_in, \
         open(output_file, 'w', encoding='utf-8') as f_out:
        
        for line in f_in:
            processed_entries += 1
            try:
                data = json.loads(line.strip())
                original_response = data['response']
                
                # 提取数值
                extracted_value = extract_number_from_response(original_response, task_id)
                
                # 检查是否成功提取数值
                # 如果提取的值是纯数字，则视为成功提取
                if re.match(r'^\d+\.?\d*$', str(extracted_value)):
                    extracted_values += 1
                    if extracted_value != original_response:
                        logging.info(f"成功提取 (任务ID: {task_id}): '{original_response}' -> '{extracted_value}'")
                    else:
                        logging.info(f"原始响应已是数值 (任务ID: {task_id}): '{original_response}'")
                elif extracted_value == 'null':
                    failed_extractions += 1
                    # 日志已在extract_number_from_response函数中记录
                else:
                    failed_extractions += 1
                    logging.warning(f"未能提取数值 (任务ID: {task_id}): '{original_response}'")
                
                # 更新响应
                data['original_response'] = original_response
                data['response'] = extracted_value
                
                # 写入处理后的数据
                f_out.write(json.dumps(data, ensure_ascii=False) + '\n')
                
            except json.JSONDecodeError:
                logging.error(f"JSON解析错误: {line}")
            except Exception as e:
                logging.error(f"处理行时出错: {str(e)}, 行内容: {line}")
    
    return processed_entries, extracted_values, failed_extractions

def process_directory(input_dir, output_dir):
    """处理目录中的所有测量结果文件"""
    processed_files = 0
    total_processed_entries = 0
    total_extracted_values = 0
    total_failed_extractions = 0
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 遍历源目录
    for task_id in os.listdir(input_dir):
        task_path = os.path.join(input_dir, task_id)
        if not os.path.isdir(task_path):
            continue
            
        # 遍历任务ID目录下的模型目录
        for model_name in os.listdir(task_path):
            model_path = os.path.join(task_path, model_name)
            if not os.path.isdir(model_path):
                continue
                
            # 遍历模型目录下的结果文件
            for filename in os.listdir(model_path):
                if not filename.endswith('.jsonl'):
                    continue
                    
                input_file = os.path.join(model_path, filename)
                output_file = os.path.join(output_dir, task_id, model_name, filename)
                
                logging.info(f"处理文件: {input_file}")
                entries, extracted, failed = process_jsonl_file(input_file, output_file, task_id)
                
                processed_files += 1
                total_processed_entries += entries
                total_extracted_values += extracted
                total_failed_extractions += failed
    
    logging.info(f"处理完成! 共处理 {processed_files} 个文件, {total_processed_entries} 条记录")
    logging.info(f"成功提取 {total_extracted_values} 个数值, 失败 {total_failed_extractions} 个")
    print(f"处理完成! 共处理 {processed_files} 个文件, {total_processed_entries} 条记录")
    print(f"成功提取 {total_extracted_values} 个数值, 失败 {total_failed_extractions} 个")
    print(f"处理后的文件保存在: {output_dir}")
    print(f"详细日志保存在: extract_measurement_values_improved.log")

def process_single_file(input_file, output_file, task_id):
    """处理单个文件"""
    logging.info(f"处理文件: {input_file}")
    entries, extracted, failed = process_jsonl_file(input_file, output_file, task_id)
    
    logging.info(f"处理完成! 共处理 {entries} 条记录")
    logging.info(f"成功提取 {extracted} 个数值, 失败 {failed} 个")
    print(f"处理完成! 共处理 {entries} 条记录")
    print(f"成功提取 {extracted} 个数值, 失败 {failed} 个")
    print(f"处理后的文件保存在: {output_file}")
    print(f"详细日志保存在: extract_measurement_values_improved.log")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='从JSONL文件中提取测量值')
    parser.add_argument('--input', type=str, required=True, help='输入JSONL文件或目录')
    parser.add_argument('--output', type=str, required=True, help='输出JSONL文件或目录')
    parser.add_argument('--task-id', type=str, help='任务ID，处理单个文件时必须提供')
    args = parser.parse_args()
    
    # 检查输入是文件还是目录
    if os.path.isfile(args.input):
        # 处理单个文件
        if not args.task_id:
            print("错误: 处理单个文件时必须提供任务ID (--task-id)")
            return
        process_single_file(args.input, args.output, args.task_id)
    elif os.path.isdir(args.input):
        # 处理目录
        process_directory(args.input, args.output)
    else:
        print(f"错误: 输入路径 {args.input} 不存在")

if __name__ == "__main__":
    main()
