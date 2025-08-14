import os
import json
import pandas as pd
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score
from datetime import datetime
#5月13日更新
# 预定义的TSV路径映射
TSV_PATH = {
        '04': '/media/ps/data-ssd/json_processing/ale_tsv_output/04.tsv',
        '17': '/media/ps/data-ssd/json_processing/ale_tsv_output/17_1.tsv',
        '23': '/media/ps/data-ssd/json_processing/ale_tsv_output/23.tsv',
        '32': '/media/ps/data-ssd/json_processing/ale_tsv_output/32_image.tsv',
        '64': '/media/ps/data-ssd/json_processing/ale_tsv_output/64.BrEaST-Lesions_USG-images_and_masks-Dec-15-2023.tsv',

        '09': '/media/ps/data-ssd/json_processing/ale_tsv_output/single_channel_seg/09.tsv',
        '13': '/media/ps/data-ssd/json_processing/ale_tsv_output/single_channel_seg/13.tsv',
        '16': '/media/ps/data-ssd/json_processing/ale_tsv_output/single_channel_seg/16.tsv',
        '18': '/media/ps/data-ssd/json_processing/ale_tsv_output/single_channel_seg/18_1.Ultrasound_Heart_Segmentation_Dataset.tsv',
        '31': '/media/ps/data-ssd/json_processing/ale_tsv_output/31.tsv',
        '37': '/media/ps/data-ssd/json_processing/ale_tsv_output/single_channel_seg/37.tsv',
        '38': '/media/ps/data-ssd/json_processing/ale_tsv_output/38.tsv',
        '47': '/media/ps/data-ssd/json_processing/ale_tsv_output/47.tsv',
        '49': '/media/ps/data-ssd/json_processing/ale_tsv_output/49.tsv',
        '50': '/media/ps/data-ssd/json_processing/ale_tsv_output/50.tsv',
        '52': '/media/ps/data-ssd/json_processing/ale_tsv_output/single_channel_seg/52.tsv',
        '53': '/media/ps/data-ssd/json_processing/ale_tsv_output/single_channel_seg/53.tsv',
        '67': '/media/ps/data-ssd/json_processing/ale_tsv_output/single_channel_seg/67.tsv',

        '48': '/media/ps/data-ssd/json_processing/ale_tsv_output/single_keypoint/48.tsv'
    }

def find_model_files(base_dir, task_id):
    """自动发现指定任务下的所有模型结果文件"""
    task_dir = os.path.join(base_dir, task_id)
    model_files = []
    
    try:
        if not os.path.exists(task_dir):
            print(f"警告：任务目录不存在 {task_dir}，跳过")
            return model_files
            
        for model_dir in os.listdir(task_dir):
            model_path = os.path.join(task_dir, model_dir)
            if os.path.isdir(model_path):
                try:
                    for file in os.listdir(model_path):
                        if file.endswith('.jsonl'):
                            full_path = os.path.join(model_path, file)
                            model_files.append((full_path, TSV_PATH[task_id]))
                except Exception as e:
                    print(f"警告：无法读取模型目录 {model_path}，错误: {e}")
                    continue
    except Exception as e:
        print(f"警告：处理任务目录 {task_dir} 时出错，错误: {e}")
    
    return model_files


def read_jsonl_with_tsv(jsonl_path, tsv_path):
    """读取JSONL文件并合并TSV中的seg_ans"""
    def extract_coordinates(keypoints_str):
        try:
            fixed_str = keypoints_str.replace("'", '"')
            data = json.loads(fixed_str)
            if isinstance(data, dict):
                return list(data.values())[0] # 这种情况下，默认只有一对坐标需要提取
            else:
                return list(data[0].values())[0] # 只取第一个
        except:
            return 'nan' 
    with open(jsonl_path, 'r') as f:
        jsonl_data = [json.loads(line) for line in f]
    df_jsonl = pd.DataFrame(jsonl_data)

    df_tsv = pd.read_csv(tsv_path, sep='\t')
    
    # 按ID匹配或行号匹配
    if 'id' in df_jsonl.columns and 'id' in df_tsv.columns:
        df_merged = pd.merge(df_jsonl, df_tsv[['id', 'seg_ans']], on='id', how='left')
    else:
        if 'keypoints' in df_tsv.columns:
            df_merged = df_jsonl.assign(seg_ans=df_tsv['keypoints'].apply(extract_coordinates))
        elif 'gt_bbox' in df_tsv.columns:
            df_merged = df_jsonl.assign(seg_ans=df_tsv['gt_bbox'].apply(extract_coordinates))
    return df_merged


def get_bounding_box_location_v1(gt_bbox):
    """
    Determines the location category of a bounding box.
    """
    import math
    if isinstance(gt_bbox, float) and math.isnan(gt_bbox): # For gt_bbox = float('nan')
        return 'not visible'
    
    # Check if gt_bbox is a sequence of expected length
    if not isinstance(gt_bbox, (list, tuple)) or len(gt_bbox) < 2: # Expecting at least center_x, center_y
        return 'not visible'

    try:
        center_x, center_y = float(gt_bbox[0]), float(gt_bbox[1])
    except (ValueError, TypeError): # Handles non-numeric values in gt_bbox
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
    

def new_seg_eval(data, jsonl_path=None):
    from sklearn.metrics import precision_score, recall_score, f1_score
    gt_list = []
    pred_list = []
    failed_items = 0
    
    # 从文件路径中提取模型名称
    model_name = os.path.basename(os.path.dirname(jsonl_path)) if jsonl_path else None
    
    for _, row in data.iterrows():
        gt_bbox = row['seg_ans']
        gt = get_bounding_box_location_v1(gt_bbox)
        
        # 检查是否有 'model' 字段，如果没有，使用从路径中提取的模型名称
        if 'model' in data.columns and len(data['model']) > 0:
            current_model = data['model'][0]
        else:
            current_model = model_name
            
        if current_model == 'LLaVA-1.5-13B-HF':
            raw_pred = row['response'].replace(' ', '', 1)
        else:
            # 获取预测结果并清理
            raw_pred = row.get('response')
        
        # 清理和提取位置信息
        if raw_pred is not None:
            # 去除换行符和首尾空格
            raw_pred = raw_pred.strip()
            # 统一转为小写
            raw_pred = raw_pred.lower()
            
            # 提取位置信息（匹配预定义的位置关键词）
            location_keywords = [
                'upper left', 'upper center', 'upper right',
                'middle left', 'center', 'middle right',
                'lower left', 'lower center', 'lower right',
                'not visible'
            ]
            
            # 尝试直接匹配
            matched = False
            for keyword in location_keywords:
                if keyword in raw_pred:
                    raw_pred = keyword
                    matched = True
                    break
            
            # 如果没有匹配到，尝试更宽松的匹配
            if not matched:
                if 'upper' in raw_pred and 'left' in raw_pred:
                    raw_pred = 'upper left'
                elif 'upper' in raw_pred and 'center' in raw_pred:
                    raw_pred = 'upper center'
                elif 'upper' in raw_pred and 'right' in raw_pred:
                    raw_pred = 'upper right'
                elif 'middle' in raw_pred and 'left' in raw_pred:
                    raw_pred = 'middle left'
                elif ('middle' in raw_pred and 'center' in raw_pred) or ('central' in raw_pred):
                    raw_pred = 'center'
                elif 'middle' in raw_pred and 'right' in raw_pred:
                    raw_pred = 'middle right'
                elif 'lower' in raw_pred and 'left' in raw_pred:
                    raw_pred = 'lower left'
                elif 'lower' in raw_pred and 'center' in raw_pred:
                    raw_pred = 'lower center'
                elif 'lower' in raw_pred and 'right' in raw_pred:
                    raw_pred = 'lower right'
                elif 'not' in raw_pred and 'visible' in raw_pred:
                    raw_pred = 'not visible'
            
            # 打印调试信息
            # print(f"原始回复: '{row.get('response')}', 提取位置: '{raw_pred}'")
        else:
            raw_pred = ''
                
        if pd.isna(raw_pred) or raw_pred == 'failed':
            failed_items += 1
            continue

        gt_list.append(gt)
        pred_list.append(raw_pred)

    total_samples = len(data) - failed_items
    if total_samples == 0:
        return {'error': 'No valid samples'}
    return {
        # 'parser_rate': total_samples / len(data),
        'acc': sum(g == p for g, p in zip(gt_list, pred_list)) / total_samples,
        # 'precision': precision_score(gt_list, pred_list, average='macro'),
        # 'recall': recall_score(gt_list, pred_list, average='macro'),
        # 'f1': f1_score(gt_list, pred_list, average='macro')
    }

def batch_evaluate_all_tasks():
    """批量处理所有任务的主函数"""
    base_dir = '/home/guohongcheng/DolphinV1.9p/seg'
    output_file = '/home/guohongcheng/DolphinV1.9p_results/seg_results.txt'
    
    all_results = []
    
    for task_id in TSV_PATH:
        task_pairs = find_model_files(base_dir, task_id)
        if not task_pairs:
            print(f"Task {task_id} skipped: no files found")
            continue
        
        for jsonl_path, tsv_path in task_pairs:
            try:
                # 读取数据
                data = read_jsonl_with_tsv(jsonl_path, tsv_path)

                # 执行评估
                metrics = new_seg_eval(data, jsonl_path=jsonl_path)
                
                # 从路径解析模型名称
                model_name = jsonl_path.split('/')[-2]  # 根据实际路径结构调整
                
                if 'error' in metrics:
                    print(f"Skipped {model_name}@{task_id}: {metrics['error']}")
                    continue
                
                # 记录结果
                all_results.append({
                    'task_id': task_id,
                    'model': model_name,
                    **metrics
                })
                print(f"Success to process {jsonl_path}")
            except Exception as e:
                print(f"Failed to process {jsonl_path}: {str(e)}")
    
    # 保存结果
    save_results(all_results, output_file)
    print(f"Evaluation completed. Results saved to {output_file}")

def save_results(results, output_file):
    """保存评估结果"""
    columns = ['task_id', 'model', 'acc']
    
    with open(output_file, 'w') as f:
        # 写入表头
        f.write('\t'.join(columns) + '\n')
        
        # 写入数据行
        for result in results:
            row = [
                result['task_id'],
                result['model'],
                f"{result['acc']:.4f}"
            ]
            f.write('\t'.join(row) + '\n')

# 保留原有的find_model_files等辅助函数

if __name__ == "__main__":
    batch_evaluate_all_tasks()
