import os
import json
import pandas as pd
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score
from datetime import datetime

# 5月26日更新 - 修复anatomy任务评分为0的问题
TSV_PATH = {
        '03': '/media/ps/data-ssd/json_processing/ale_tsv_output/classification_tsv_output/3_FETAL_Planes_US.tsv',
        '37': '/media/ps/data-ssd/json_processing/ale_tsv_output/37.tsv',
        '50': '/media/ps/data-ssd/json_processing/ale_tsv_output/classification_tsv_output/50.ACOUSLIC_AI_Key_Frame_Classification_is_optimal_or_suboptimal.tsv',
        '53': '/media/ps/data-ssd/json_processing/ale_tsv_output/53.tsv',
        '69': '/media/ps/data-ssd/json_processing/ale_tsv_output/classification_tsv_output/69.tsv',
        '10': '/media/ps/data-ssd/json_processing/ale_tsv_output/classification_tsv_output/10_FetusOrientation.tsv',
        '18': '/media/ps/data-ssd/json_processing/ale_tsv_output/classification_tsv_output/18_1.Ultrasound_Heart_Segmentation_Dataset_view.tsv',
        '21': '/media/ps/data-ssd/json_processing/ale_tsv_output/21.Breast_Ultrasound_Segmentation_Dataset.tsv',
        '23': '/media/ps/data-ssd/json_processing/ale_tsv_output/23.tsv',
        '25': '/media/ps/data-ssd/json_processing/ale_tsv_output/25.Dermatologic_Ultrasound_Classification_Dataset.tsv',
        '28': '/media/ps/data-ssd/json_processing/ale_tsv_output/classification_tsv_output/28_1.Knee_Grading_Ultrasound_Classification_Dataset_Kellgren-Lawrence (KL) Grade.tsv',
        '32': '/media/ps/data-ssd/json_processing/ale_tsv_output/32_image.tsv',
        '40': '/media/ps/data-ssd/json_processing/ale_tsv_output/classification_tsv_output/40_birads.tsv',
        '42': '/media/ps/data-ssd/json_processing/ale_tsv_output/42.tsv',
        '44': '/media/ps/data-ssd/json_processing/ale_tsv_output/44.COVID-BLUES-frames.tsv',
        '57': '/media/ps/data-ssd/json_processing/ale_tsv_output/57_1.Liver_Ultrasound_Segmentation_Dataset.tsv',
        '66': '/media/ps/data-ssd/json_processing/ale_tsv_output/66.tsv',
        '70': '/media/ps/data-ssd/json_processing/ale_tsv_output/70.tsv',
        '75': '/media/ps/data-ssd/json_processing/ale_tsv_output/75.PCOS_Ultrasound_Classification_Dataset.tsv',
        '74is_normal': '/media/ps/data-ssd/json_processing/ale_tsv_output/classification_tsv_output/74_is_normal.tsv',
        '74is_visible': '/media/ps/data-ssd/json_processing/ale_tsv_output/classification_tsv_output/74_is_visible.tsv',
        'anatomy': '/media/ps/data-ssd/json_processing/ale_tsv_output/classification_tsv_output/anatomy.tsv',
        '28_class': '/media/ps/data-ssd/json_processing/ale_tsv_output/28.Knee_Classification.tsv'
    }


def read_jsonl_with_tsv(jsonl_path, tsv_path, task_id=None):
    """读取JSONL文件并合并对应TSV文件的class值，增强对anatomy任务的处理"""
    # 读取JSONL
    jsonl_data = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            jsonl_data.append(json.loads(line.strip()))
    df_jsonl = pd.DataFrame(jsonl_data)

    # 读取TSV
    df_tsv = pd.read_csv(tsv_path, sep='\t')
    
    # 针对anatomy任务的特殊处理
    if task_id == 'anatomy':
        try:
            # 尝试从classes字段中提取Anatomy值
            classes_data = []
            for _, row in df_tsv.iterrows():
                if 'classes' in df_tsv.columns:
                    classes_value = row['classes']
                    if isinstance(classes_value, str):
                        # 尝试解析JSON字符串
                        try:
                            classes_dict = json.loads(classes_value.replace("'", '"'))
                            if isinstance(classes_dict, dict) and 'Anatomy' in classes_dict:
                                classes_data.append(classes_dict['Anatomy'].lower())
                            else:
                                classes_data.append(classes_value.lower())
                        except json.JSONDecodeError:
                            # 如果解析失败，尝试使用正则表达式提取
                            import re
                            match = re.search(r'"Anatomy":\s*"([^"]+)"', classes_value)
                            if match:
                                classes_data.append(match.group(1).lower())
                            else:
                                classes_data.append(classes_value.lower())
                    else:
                        classes_data.append(str(classes_value).lower())
                else:
                    classes_data.append('')
            
            # 将提取的Anatomy值赋给df_jsonl
            df_jsonl['cla_ans'] = classes_data
            print(f"成功处理anatomy任务，提取了{len(classes_data)}个解剖结构名称")
            
        except Exception as e:
            print(f"处理anatomy任务时出错: {e}")
            # 回退到默认处理方式
            if 'classes' in df_tsv.columns:
                df_jsonl['cla_ans'] = df_tsv['classes'].values  
            else:
                df_jsonl['cla_ans'] = df_tsv['class'].values
    else:
        # 按行号合并（假设行号严格对应）
        if 'id' not in df_jsonl.columns or 'id' not in df_tsv.columns:
            if 'classes' in df_tsv.columns:
                df_jsonl['cla_ans'] = df_tsv['classes'].values  
            else:
                df_jsonl['cla_ans'] = df_tsv['class'].values  
        else:
            # 按ID精确匹配
            df_merged = pd.merge(df_jsonl, df_tsv[['id', 'classes']], 
                               on='id', how='left', suffixes=('', '_tsv'))
            df_jsonl['cla_ans'] = df_merged['class']

    return df_jsonl

def model_eval(data, jsonl_path=None):
    """更新后的评估函数，增强对不同格式回复的处理能力"""
    failed_items = 0
    y_true = []
    y_pred = []
    
    # 从文件路径中提取模型名称
    model_name = os.path.basename(os.path.dirname(jsonl_path)) if jsonl_path else None

    for i, row in data.iterrows():
        # 检查是否有 'model' 字段，如果没有，使用从路径中提取的模型名称
        if 'model' in data.columns and len(data['model']) > 0:
            current_model = data['model'][0]
        else:
            current_model = model_name
        
        # 处理预测结果，去除换行符和首尾空格
        if current_model == 'LLaVA-1.5-13B-HF':
            pred = row['response'].replace(' ', '', 1)
        else:
            pred = row['response']
        
        # 清理预测结果：去除换行符、首尾空格和引号
        pred = pred.strip().strip("'\"")
        
        if isinstance(row['cla_ans'], str):
            # 清理参考答案
            true_ans = row['cla_ans']
            if '[' in true_ans:
                true_ans = true_ans.replace('[','').replace(']','')
            
            # 统一转为小写并去除首尾空格和引号
            true_ans = true_ans.lower().strip().strip("'\"")
            pred_ans = pred.lower()
            
            # 打印调试信息
            # print(f"真实答案: '{true_ans}', 预测答案: '{pred_ans}'")
            
            y_true.append(true_ans)  
            y_pred.append(pred_ans)
        elif isinstance(row['cla_ans'], int):
            try:
                # 尝试将预测结果转为整数
                pred = int(pred)
            except:
                failed_items += 1
                continue
            y_true.append(row['cla_ans']) 
            y_pred.append(pred)
        else:
            y_true.append(row['cla_ans'])  
            y_pred.append(pred)

    # 计算指标
    total_samples = len(data) - failed_items
    if total_samples == 0:
        print("警告：没有有效的样本进行评估")
        return {
            'parser_rate': 0.0,
            'acc': 0.0,
            'precision': 0.0,
            'recall': 0.0,
            'f1': 0.0
        }
    
    # 打印一些样本进行调试
    print(f"样本总数: {len(data)}, 有效样本: {total_samples}, 失败样本: {failed_items}")
    if len(y_true) > 0:
        print(f"前5个真实答案: {y_true[:5]}")
        print(f"前5个预测答案: {y_pred[:5]}")
    
    return {
        'parser_rate': total_samples / len(data),
        'acc': sum(np.array(y_true) == np.array(y_pred)) / total_samples,
        'precision': precision_score(y_true, y_pred, average='macro'),
        'recall': recall_score(y_true, y_pred, average='macro'),
        'f1': f1_score(y_true, y_pred, average='macro')
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

def batch_evaluate_all_tasks():
    """批量处理所有任务的主函数"""
    base_dir = '/media/ps/data-ssd/benchmark/VLMEvalKit/outputs/dolphin-output/cla'
    output_file = f'cla_results_{datetime.now().strftime("%Y%m%d_%H%M")}.txt'
    
    all_results = []

    # 遍历所有预定义的任务
    for task_id in TSV_PATH.keys():
        print(f"正在评估任务 {task_id}...")
        # 自动发现该任务下的所有模型文件
        task_pairs = find_model_files(base_dir, task_id)
        
        if not task_pairs:
            print(f"警告：任务 {task_id} 未找到任何模型结果文件")
            continue
        
        # 执行评估
        task_results = evaluate_task(task_pairs, task_id)
        all_results.extend(task_results)
    
    # 写入统一结果文件
    write_combined_results(all_results, output_file)
    print(f"评估完成，结果已保存到 {output_file}")

def evaluate_task(file_pairs, task_id):
    """评估单个任务下的所有模型"""
    task_results = []
    
    for jsonl_path, tsv_path in file_pairs:
        try:
            # 从文件路径解析模型名称
            model_name = jsonl_path.split('/')[-2]  # 根据实际路径结构调整索引
            print(f"正在评估模型 {model_name}...")
            
            # 传递task_id参数，以便对anatomy任务进行特殊处理
            data = read_jsonl_with_tsv(jsonl_path, tsv_path, task_id=task_id)

            metrics = model_eval(data, jsonl_path=jsonl_path)
            
            # 记录附加信息
            metrics.update({
                'task_id': task_id,
                'model': model_name,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            task_results.append(metrics)
            
            # 打印评估结果
            print(f"模型 {model_name} 评估结果:")
            print(f"  准确率: {metrics['acc']:.4f}")
            print(f"  精确率: {metrics['precision']:.4f}")
            print(f"  召回率: {metrics['recall']:.4f}")
            print(f"  F1分数: {metrics['f1']:.4f}")
            
        except Exception as e:
            print(f"处理文件失败：{jsonl_path}")
            print(f"错误信息：{str(e)}")
            import traceback
            traceback.print_exc()
    
    return task_results

def write_combined_results(results, output_file):
    """写入整合后的结果"""
    columns = [
        'task_id', 'model', 'timestamp',
        'parser_rate', 'acc', 'precision', 'recall', 'f1'
    ]
    
    with open(output_file, 'w') as f:
        # 写入表头
        f.write("\t".join(columns) + "\n")
        
        # 写入数据行
        for res in results:
            line = "\t".join([
                res['task_id'],
                res['model'],
                res['timestamp'],
                f"{res['parser_rate']:.4f}",
                f"{res['acc']:.4f}",
                f"{res['precision']:.4f}",
                f"{res['recall']:.4f}",
                f"{res['f1']:.4f}"
            ]) + "\n"
            f.write(line)

def evaluate_single_task(task_id):
    """评估单个指定的任务"""
    base_dir = '/media/ps/data-ssd/benchmark/VLMEvalKit/outputs/dolphin-output/cla'
    output_file = f'cla_{task_id}_results_{datetime.now().strftime("%Y%m%d_%H%M")}.txt'
    
    print(f"正在评估任务 {task_id}...")
    
    if task_id not in TSV_PATH:
        print(f"错误：未找到任务 {task_id} 的TSV路径定义")
        return
    
    # 自动发现该任务下的所有模型文件
    task_pairs = find_model_files(base_dir, task_id)
    
    if not task_pairs:
        print(f"警告：任务 {task_id} 未找到任何模型结果文件")
        return
    
    # 执行评估
    task_results = evaluate_task(task_pairs, task_id)
    
    # 写入结果文件
    write_combined_results(task_results, output_file)
    print(f"评估完成，结果已保存到 {output_file}")

if __name__ == "__main__":
    # 可以选择评估所有任务或单个任务
    # batch_evaluate_all_tasks()
    
    # 或者只评估anatomy任务
    evaluate_single_task('anatomy')
