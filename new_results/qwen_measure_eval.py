import os
import json
import pandas as pd
import numpy as np
import re
from sklearn.metrics import precision_score, recall_score, f1_score
from datetime import datetime
import pingouin as pg
#5月13日更新
# 预定义的TSV路径映射, 31单独测评
TSV_PATH = {
        '18': '/media/ps/data-ssd/json_processing/ale_tsv_output/18_1.Ultrasound_Heart_Segmentation_Dataset.tsv',
        '27': '/media/ps/data-ssd/json_processing/ale_tsv_output/27.tsv',
        # '31': '/media/ps/data-ssd/json_processing/ale_tsv_output/31.tsv',
        '50': '/media/ps/data-ssd/json_processing/ale_tsv_output/50.tsv',
        '57': '/media/ps/data-ssd/json_processing/ale_tsv_output/57_1.Liver_Ultrasound_Segmentation_Dataset.tsv'
    }

MIN_MAX_DICT = {
    '18': {'min': 10.0, 'max': 75.0},
    '27': {'min': 0.3, 'max': 1.5},
    '50': {'min': 100.0, 'max': 400.0},
    '57': {'min': 0, 'max': 85},
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


def read_jsonl_with_tsv(jsonl_path, tsv_path, task_id):
    """读取JSONL文件并合并TSV中的ans"""
    def extract_mea(measurements_str):
        try:
            fixed_str = measurements_str.replace("'", '"')
            data = json.loads(fixed_str)
            if isinstance(data, dict):
                if task_id == '18':
                    return data['EF']
                elif task_id == '27':
                    return list(data['IMT'])[0]
                elif task_id == '31':
                    return data
                elif task_id == '50':
                    return data['abdominal_circumference']
                else:
                    return data['fat value']
            elif isinstance(data, list):
                return list(data[0].values())[0]
        except:
            return 'nan' 

    with open(jsonl_path, 'r') as f:
        jsonl_data = [json.loads(line) for line in f]
    df_jsonl = pd.DataFrame(jsonl_data)

    df_tsv = pd.read_csv(tsv_path, sep='\t')

    if 'id' in df_jsonl.columns and 'id' in df_tsv.columns:
        df_merged = pd.merge(df_jsonl, df_tsv[['id', 'measurement_ans']], on='id', how='left')
    else:
        df_merged = df_jsonl.assign(measurement_ans=df_tsv['measurement'].apply(extract_mea))
    return df_merged

def extract_number(text):
    """从文本中提取数值。如果是'null'，返回None。"""
    if text is None or text.lower() == 'null':
        return None
    
    # 尝试直接转换为浮点数
    try:
        return float(text)
    except ValueError:
        pass
    
    # 尝试使用正则表达式提取数字
    number_patterns = [
        r'(\d+\.\d+)',  # 浮点数
        r'(\d+)',       # 整数
    ]
    
    for pattern in number_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue
    
    return None

def min_max_scale(y_arr, task_id):
    min_val = MIN_MAX_DICT[task_id]['min']
    max_val = MIN_MAX_DICT[task_id]['max']

    if max_val == min_val:
        return np.zeros_like(y_arr, dtype=float)
    else:
        return (y_arr - min_val) / (max_val - min_val)
    
def meaeval(data: pd.DataFrame, task_id: str, jsonl_path: str = None, **judge_kwargs) -> dict:  
    y_true = []
    y_pred = []
    failed_items = 0
    
    # 从文件路径中提取模型名称
    model_name = os.path.basename(os.path.dirname(jsonl_path)) if jsonl_path else None
    
    for _, row in data.iterrows():
        if isinstance(row['measurement_ans'], list):
            gt = row['measurement_ans'][0]
        else:
            gt = row['measurement_ans']
        if gt == 'nan':
            continue

        # 检查是否有 'model' 字段，如果没有，使用从路径中提取的模型名称
        if 'model' in data.columns and len(data['model']) > 0:
            current_model = data['model'][0]
        else:
            current_model = model_name
            
        if current_model == 'LLaVA-1.5-13B-HF':
            pred_text = row['response'].replace(' ', '', 1)
        else:
            pred_text = row['response']
        
        # 清理预测文本：去除换行符和首尾空格
        if pred_text is not None:
            pred_text = pred_text.strip()
        
        try:
            # 提取数值
            pred = extract_number(pred_text)
        except:
            failed_items += 1
            continue
        
        if pred is None:
            failed_items += 1
            continue
        
        y_true.append(float(gt))
        y_pred.append(pred)
        print(f'task: {task_id}, gt: {gt}, pred: {pred}')
    # 添加正则化
    y_true = np.array(y_true)
    y_true = min_max_scale(y_true, task_id)
    y_pred = np.array(y_pred)
    y_pred = min_max_scale(y_pred, task_id)
    errors = y_true - y_pred
    tolerance = 0.1
    tolerance = judge_kwargs.get('tolerance', 0.1)
    
    metrics = {
        'MAE': np.mean(np.abs(errors)),
        'RMSE': np.sqrt(np.mean(errors**2)),
        'Std': np.std(errors),
        '%_within_tolerance': np.mean(np.abs(errors) <= tolerance) * 100,
        'failed_items': failed_items
    }
    
    # # ICC计算（需构造评分者矩阵）
    # icc_data = pd.DataFrame({
    #         'target': np.repeat(np.arange(len(y_true)), 2),
    #         'rater': np.tile(['true', 'pred'], len(y_true)),
    #         'score': np.column_stack([y_true, y_pred]).flatten()
    #     })
    
    # try:
    #     icc_result = pg.intraclass_corr(
    #         data=icc_data,
    #         targets='target',
    #         raters='rater',
    #         ratings='score'
    #     ).set_index('Type')
        
    #     metrics['ICC(3,1)'] = icc_result.loc['ICC3k', 'ICC']
    # except:
    #     metrics['ICC(3,1)'] = None  # 数据不足时返回空值
            
    return metrics

def batch_evaluate_all_tasks():
    """批量处理所有任务的主函数"""
    base_dir = '/home/guohongcheng/DolphinV1.9p/measurement_processed'
    output_file = '/home/guohongcheng/DolphinV1.9p_results/mea_results.txt'
    
    all_results = []
    
    for task_id in TSV_PATH:
        task_pairs = find_model_files(base_dir, task_id)
        if not task_pairs:
            print(f"Task {task_id} skipped: no files found")
            continue
        
        for jsonl_path, tsv_path in task_pairs:
            # try:
            # 读取数据
                data = read_jsonl_with_tsv(jsonl_path, tsv_path, task_id)

                # 从路径解析模型名称
                model_name = jsonl_path.split('/')[-2]  # 根据实际路径结构调整
                
                # 执行评估
                if task_id == '31':
                   continue
                else:
                    metrics = meaeval(data, task_id, jsonl_path=jsonl_path)
                    if 'error' in metrics:
                        print(f"Skipped {model_name}@{task_id}: {metrics['error']}")
                        continue

                    all_results.append({
                        'task_id': task_id,
                        'model': model_name,
                        **metrics
                    })
                    print(f"Success to process {jsonl_path}")
            # except Exception as e:
            #     print(f"Failed to process {jsonl_path}: {str(e)}")
    
    # 保存结果
    save_results(all_results, output_file)
    print(f"Evaluation completed. Results saved to {output_file}")

def save_results(results, output_file):
    """保存评估结果"""
    columns = ['task_id', 'model', 'RMSE', 'MAE', 'Std', '%_within_tolerance', 'failed_items']
    
    with open(output_file, 'w') as f:
        # 写入表头
        f.write('\t'.join(columns) + '\n')
        
        # 写入数据行
        for result in results:
            row = [
                result['task_id'],
                result['model'],
                f"{result['RMSE']:.4f}",
                f"{result['MAE']:.4f}",
                f"{result['Std']:.4f}",
                f"{result['%_within_tolerance']:.4f}",
                str(result['failed_items'])
            ]
            f.write('\t'.join(row) + '\n')


if __name__ == "__main__":
    batch_evaluate_all_tasks()
