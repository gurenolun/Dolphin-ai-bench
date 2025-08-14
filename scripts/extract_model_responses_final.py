#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re
import argparse
from pathlib import Path
import os
import glob

def normalize_text(text):
    """标准化文本，处理空格、换行符和大小写"""
    if not text:
        return ""
    # 转换为小写
    text = text.lower()
    # 替换换行符为空格
    text = re.sub(r'\n', ' ', text)
    # 替换多个空格为单个空格
    text = re.sub(r'\s+', ' ', text)
    # 去除首尾空格
    text = text.strip()
    # 去除引号
    text = re.sub(r'^[\'\"]+|[\'\"]+$', '', text)
    return text

# def extract_options_from_question(question):
#     """从问题中提取选项列表"""
#     options = []
#     for item in question:
#         if item.get('type') == 'text':
#             text = item.get('value', '')
#             # 处理 BI-RADS 特殊情况
#             if 'bi-rads' in text.lower():
#                 birads_options = ['2', '3', '4A', '4B', '4C', '5']
#                 if any(opt in text for opt in birads_options):
#                     return birads_options
#             # 查找选项部分
#             if 'options:' in text.lower() or 'options：' in text.lower() or 'options' in text.lower():
#                 # 尝试匹配引号中的选项列表
#                 # 先尝试匹配 options: 'option1', 'option2', 'option3' 这种格式
#                 opts_pattern = r"options:?\s*['\"](.*?)['\"](,\s*['\"](.*?)['\"])*"
#                 opts_match = re.search(opts_pattern, text, re.IGNORECASE)
                
#                 if opts_match:
#                     # 提取所有引号中的选项
#                     quoted_options = re.findall(r"['\"]([^'\"]*?)['\"]", opts_match.group(0))
#                     if quoted_options:
#                         options = [opt.strip() for opt in quoted_options]
                        

#                 # 如果上面的方法没找到足够的选项，尝试其他方式
#                 # 尝试匹配冒号后的整行文本
#                 if len(options) <= 1:
#                     opts_match = re.search(r'options:?\s*(.*?)(?:\n|$)', text, re.IGNORECASE)
#                     if opts_match:
#                         opts_text = opts_match.group(1).strip()
                        
#                         # 如果选项文本包含引号，提取引号中的内容
#                         if "'" in opts_text or '"' in opts_text:
#                             quoted_options = re.findall(r"['\"]([^'\"]*?)['\"]", opts_text)
#                             if quoted_options:
#                                 options = [opt.strip() for opt in quoted_options]
                        
#                         # 处理逗号分隔的选项
#                         if len(options) <= 1 and ',' in opts_text:
#                             # 先尝试修复缺少引号的情况
#                             fixed_opts_text = re.sub(r'([^\'"])(,)([^\'"])', r'\1"\2"\3', opts_text)
#                             options = [opt.strip().strip("'\"") for opt in fixed_opts_text.split(',')]
                            
#                         # 处理空格分隔的选项
#                         elif len(options) <= 1 and ' ' in opts_text:
#                             options = [opt.strip().strip("'\"") for opt in opts_text.split()]
                
#                 # 特殊处理：检查是否有缺少引号的选项
#                 if 'fetal brain' in text.lower() and 'fetal brain' not in [opt.lower() for opt in options]:
#                     options.append('fetal brain')
                
#                 # 特殊处理：检查常见的超声选项
#                 common_options = ['maternal cervix', 'fetal abdomen', 'fetal femur', 'fetal thorax', 'fetal brain', 'other']
#                 for opt in common_options:
#                     if opt in text.lower() and opt not in [o.lower() for o in options]:
#                         options.append(opt)
                
#                 # 如果找到了选项，返回
#                 if options:
#                     return options
            
#             # 对于seg任务，提取Location Options
#             if 'Location Options:' in text or 'following list:' in text.lower():
#                 # 尝试多种匹配模式
#                 location_match = re.search(r'Location Options:\s*(.*?)(?:\n|$)', text)
#                 if not location_match:
#                     location_match = re.search(r'following list:\s*(.*?)(?:\n|$)', text, re.IGNORECASE)
                
#                 if location_match:
#                     locations = location_match.group(1).strip().rstrip('.')  # 移除末尾的句点
#                     # 处理不同的分隔符
#                     if ', ' in locations:
#                         options = [loc.strip() for loc in locations.split(', ')]
#                     elif ',' in locations:
#                         options = [loc.strip() for loc in locations.split(',')]
#                     else:
#                         options = [loc.strip() for loc in locations.split()]
#                     return options
def extract_options_from_question(question):
    """从问题中提取选项列表"""
    options = []
    for item in question:
        if item.get('type') != 'text':
            continue
        text = item.get('value', '')

        # BI-RADS 特殊处理
        if 'bi-rads' in text.lower():
            birads_options = ['2', '3', '4A', '4B', '4C', '5']
            if any(opt in text for opt in birads_options):
                return birads_options

        if 'options:' in text.lower() or 'options：' in text.lower() or 'options' in text.lower():
            # 尝试匹配引号中的选项列表
            # 先尝试匹配 options: 'option1', 'option2', 'option3' 这种格式
            opts_pattern = r"options:?\s*['\"](.*?)['\"](,\s*['\"](.*?)['\"])*"
            opts_match = re.search(opts_pattern, text, re.IGNORECASE)
        
            if opts_match:
                # 提取所有引号中的选项
                quoted_options = re.findall(r"['\"]([^'\"]*?)['\"]", opts_match.group(0))
                if quoted_options:
                    options = [opt.strip() for opt in quoted_options]
                

            # 如果上面的方法没找到足够的选项，尝试其他方式
            # 尝试匹配冒号后的整行文本
            if len(options) <= 1:
                opts_match = re.search(r'options:?\s*(.*?)(?:\n|$)', text, re.IGNORECASE)
                if opts_match:
                    opts_text = opts_match.group(1).strip()
                
                    # 如果选项文本包含引号，提取引号中的内容
                    if "'" in opts_text or '"' in opts_text:
                        quoted_options = re.findall(r"['\"]([^'\"]*?)['\"]", opts_text)
                        if quoted_options:
                            options = [opt.strip() for opt in quoted_options]
                
                    # 处理逗号分隔的选项
                    if len(options) <= 1 and ',' in opts_text:
                        # 先尝试修复缺少引号的情况
                        fixed_opts_text = re.sub(r'([^\'"])(,)([^\'"])', r'\1"\2"\3', opts_text)
                        options = [opt.strip().strip("'\"") for opt in fixed_opts_text.split(',')]
                    
                    # 处理空格分隔的选项
                    elif len(options) <= 1 and ' ' in opts_text:
                        options = [opt.strip().strip("'\"") for opt in opts_text.split()]
        
            # 特殊处理：检查是否有缺少引号的选项
            if 'fetal brain' in text.lower() and 'fetal brain' not in [opt.lower() for opt in options]:
                options.append('fetal brain')
        
            # 特殊处理：检查常见的超声选项
            common_options = ['maternal cervix', 'fetal abdomen', 'fetal femur', 'fetal thorax', 'fetal brain', 'other']
            for opt in common_options:
                if opt in text.lower() and opt not in [o.lower() for o in options]:
                    options.append(opt)
        
            # 如果找到了选项，返回
            if options:
                return options
    
        # 对于seg任务，提取Location Options
        if 'Location Options:' in text or 'following list:' in text.lower():
            # 尝试多种匹配模式
            location_match = re.search(r'Location Options:\s*(.*?)(?:\n|$)', text)
            if not location_match:
                location_match = re.search(r'following list:\s*(.*?)(?:\n|$)', text, re.IGNORECASE)
        
            if location_match:
                locations = location_match.group(1).strip().rstrip('.')  # 移除末尾的句点
                # 处理不同的分隔符 - 修复：确保每个选项都正确清理空格和标点
                if ', ' in locations:
                    options = [loc.strip().rstrip('.').strip() for loc in locations.split(', ')]
                elif ',' in locations:
                    options = [loc.strip().rstrip('.').strip() for loc in locations.split(',')]
                else:
                    options = [loc.strip().rstrip('.').strip() for loc in locations.split()]
    return options
#         # 通用 Options 提取
#         if 'options:' in text.lower() or 'options：' in text.lower():
#             python_list_match = re.search(r'options:?\s*\[(.*?)\]', text, re.IGNORECASE)
#             if python_list_match:
#                 list_content = python_list_match.group(1)
#                 quoted_options = re.findall(r"['\"]([^'\"]*?)['\"]", list_content)
#                 if quoted_options:
#                     return [opt.strip() for opt in quoted_options]

#             # 尝试直接提取冒号后的文本
#             opts_match = re.search(r'options:?\s*(.*?)(?:\n|$)', text, re.IGNORECASE)
#             if opts_match:
#                 opts_text = opts_match.group(1).strip()
#                 quoted_options = re.findall(r"['\"]([^'\"]*?)['\"]", opts_text)
#                 if quoted_options:
#                     return [opt.strip() for opt in quoted_options]
#                 elif ',' in opts_text:
#                     return [opt.strip().strip("'\"") for opt in opts_text.split(',')]
#                 elif ' ' in opts_text:
#                     return [opt.strip().strip("'\"") for opt in opts_text.split()]
# #                 # 特殊处理：检查是否有缺少引号的选项
# #                 if 'fetal brain' in text.lower() and 'fetal brain' not in [opt.lower() for opt in options]:
# #                     options.append('fetal brain')        
#         # 超声 anatomy 类特殊值兜底
#         common_options = ['maternal cervix', 'fetal abdomen', 'fetal femur', 'fetal thorax', 'fetal brain', 'other']
#         for opt in common_options:
#             if opt in text.lower() and opt not in [o.lower() for o in options]:
#                 options.append(opt)

#         if 'fetal brain' in text.lower() and 'fetal brain' not in options:
#             options.append('fetal brain')

#         # 特定任务 Location Options
#         if 'Location Options:' in text or 'following list:' in text.lower():
#             match = re.search(r'(Location Options:|following list:)\s*(.*?)(?:\n|$)', text, re.IGNORECASE)
#             if match:
#                 loc_text = match.group(2).strip().rstrip('.')
#                 if ', ' in loc_text:
#                     return [x.strip() for x in loc_text.split(', ')]
#                 elif ',' in loc_text:
#                     return [x.strip() for x in loc_text.split(',')]
#                 else:
#                     return [x.strip() for x in loc_text.split()]

#     return options




def extract_prediction_from_response(response, options):
    """从模型回复中提取预测值"""
    if not response or not options:
        return ""
        
    # 标准化回复文本
    response_normalized = normalize_text(response)
    
    # 标准化选项文本
    normalized_options = [normalize_text(opt) for opt in options]
    
    # 1. 首先尝试直接匹配原始回复（不区分大小写）
    for i, opt in enumerate(options):
        if opt.lower() == response.lower().strip():
            return opt
   
    
    # 3. 检查多词选项的匹配
    multi_word_options = [(opt, norm) for opt, norm in zip(options, normalized_options) if ' ' in norm]
    if multi_word_options:
        for opt, opt_norm in multi_word_options:
            # 使用正则表达式匹配完整的短语（考虑词边界）
            pattern = r'\b' + re.escape(opt_norm) + r'\b'
            if re.search(pattern, response_normalized):
                return opt
            
            # 检查引号中的选项
            quote_pattern = r"['\"]" + re.escape(opt_norm) + r"['\"]"  
            if re.search(quote_pattern, response_normalized):
                return opt
            
            # 检查常见的上下文模式
            context_patterns = [
                r"is (?:a |an |the |)(?:typical for |indicative of |suggestive of |consistent with |compatible with |showing |demonstrates |revealing |)['\"]?" + re.escape(opt_norm) + r"['\"]?",
                r"(?:appears to be|identified as|classified as|recognized as|interpreted as|diagnosed as|confirmed as|representing|shows|demonstrates) (?:a |an |the |)['\"]?" + re.escape(opt_norm) + r"['\"]?",
                r"(?:the |)(?:image|ultrasound|scan|examination|visualization|assessment|analysis|interpretation|finding|result|picture|sonogram|sonographic features) (?:is |shows |demonstrates |reveals |indicates |suggests |points to |confirms |indicate |)(?:a |an |the |)['\"]?" + re.escape(opt_norm) + r"['\"]?"
            ]
            
            for pattern in context_patterns:
                if re.search(pattern, response_normalized):
                    return opt
    
    # 4. 检查单词选项的匹配（只有在没有多词选项匹配的情况下）
    single_word_options = [(opt, norm) for opt, norm in zip(options, normalized_options) if ' ' not in norm]
    for opt, opt_norm in single_word_options:
        pattern = r'\b' + re.escape(opt_norm) + r'\b'
        if re.search(pattern, response_normalized):
            # 检查这个单词选项是否是多词选项的一部分
            is_part_of_multi_word = False
            for _, multi_opt_norm in multi_word_options:
                if opt_norm in multi_opt_norm.split():
                    # 检查回复中是否包含完整的多词选项
                    if any(re.search(r'\b' + re.escape(m_norm) + r'\b', response_normalized) for _, m_norm in multi_word_options):
                        is_part_of_multi_word = True
                        break
            
            if not is_part_of_multi_word:
                return opt
    
    # 5. 如果以上都没有匹配到，尝试部分匹配
    for i, opt_norm in enumerate(normalized_options):
        if opt_norm in response_normalized:
            return options[i]

    
    # 6. 特殊处理：检查首字母大写的情况
    response_words = response.split()
    for word in response_words:
        word_lower = word.lower().strip(".,;:!?'\"")
        for i, opt in enumerate(options):
            if word_lower == opt.lower():
                return opt
            # 检查多词选项的第一个词
            opt_parts = opt.lower().split()
            if opt_parts and word_lower == opt_parts[0]:
                # 检查是否后续词也匹配
                if len(response_words) > response_words.index(word) + len(opt_parts) - 1:
                    match = True
                    for j, part in enumerate(opt_parts[1:], 1):
                        next_word = response_words[response_words.index(word) + j].lower().strip(".,;:!?'\"")
                        if next_word != part:
                            match = False
                            break
                    if match:
                        return opt
    
    # 7. 特殊处理：maternal cervix 和其他常见选项
    common_mappings = {
        'maternal': 'maternal cervix',
        'cervix': 'maternal cervix',
        'maternal cervical': 'maternal cervix',
        'fetal': 'fetal brain',  # 默认映射，如果没有更具体的匹配
        'abdomen': 'fetal abdomen',
        'femur': 'fetal femur',
        'thorax': 'fetal thorax',
        'brain': 'fetal brain'
    }
    
    for key, value in common_mappings.items():
        if key in response_normalized and value in options:
            # 检查是否有更具体的匹配
            more_specific = False
            for opt in options:
                if key in opt.lower() and opt.lower() != value.lower() and opt.lower() in response_normalized:
                    more_specific = True
                    break
            if not more_specific:
                return value
    
    return ""

def process_single_file(input_file, output_file, debug=False):
    """处理单个JSONL文件并将结果写入输出文件"""
    with open(input_file, 'r', encoding='utf-8') as f_in, open(output_file, 'w', encoding='utf-8') as f_out:
        for line_num, line in enumerate(f_in):
            try:
                data = json.loads(line.strip())
                question = data.get('question', [])
                response = data.get('response', '')
                
                # 提取选项列表
                options = extract_options_from_question(question)
                
                if debug:
                    print(f"\n行 {line_num+1}:")
                    print(f"选项: {options}")
                    print(f"回复: {response}")
                
                # 如果有选项，尝试从回复中提取预测值
                prediction = ""
                if options:
                    prediction = extract_prediction_from_response(response, options)
                    if debug:
                        print(f"提取的预测值: {prediction}")
                    
                    # 更新数据中的回复
                    data['response'] = prediction
                    # 保存原始回复
                    data['original_response'] = response
                else:
                    if debug:
                        print("警告: 未找到选项")
                
                # 写入输出文件
                f_out.write(json.dumps(data, ensure_ascii=False) + '\n')
            except Exception as e:
                print(f"处理文件 {input_file} 行 {line_num+1} 时出错: {str(e)}")

def process_directory(input_dir, output_dir, debug=False):
    """处理目录中的所有JSONL文件"""
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有JSONL文件
    jsonl_files = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.jsonl'):
                jsonl_files.append(os.path.join(root, file))
    
    # 处理每个文件
    for input_file in jsonl_files:
        # 构建输出文件路径，保持相对路径结构
        rel_path = os.path.relpath(input_file, input_dir)
        output_file = os.path.join(output_dir, rel_path)
        
        # 确保输出文件的目录存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 处理文件
        process_single_file(input_file, output_file, debug)
        print(f"已处理: {input_file} -> {output_file}")

def main():
    parser = argparse.ArgumentParser(description='从JSONL文件中提取模型回复')
    parser.add_argument('--input', type=str, required=True, help='输入JSONL文件或目录')
    parser.add_argument('--output', type=str, required=True, help='输出JSONL文件或目录')
    parser.add_argument('--debug', action='store_true', help='启用调试模式，打印详细信息')
    args = parser.parse_args()
    
    # 检查输入是文件还是目录
    if os.path.isfile(args.input):
        # 处理单个文件
        process_single_file(args.input, args.output, args.debug)
        print(f"已处理: {args.input} -> {args.output}")
    elif os.path.isdir(args.input):
        # 处理目录
        process_directory(args.input, args.output, args.debug)
    else:
        print(f"错误: 输入路径 {args.input} 不存在")

if __name__ == "__main__":
    main()
