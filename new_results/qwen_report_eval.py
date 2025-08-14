import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from pycocoevalcap.bleu.bleu import Bleu 
from pycocoevalcap.rouge.rouge import Rouge 
from transformers import AutoTokenizer, AutoModel
import torch
#5月13日更新
# 配置参数
HAVE_LOCAL_BERTSCORE_MODEL = False
LOCAL_MODEL_DIR = "/path/to/models"
BERTSCORE_MODEL_NAME = "bert-base-multilingual-cased"
TSV_PATH = {
    '10': '/media/ps/data-ssd/json_processing/ale_tsv_output/10.tsv',
    '11': '/media/ps/data-ssd/json_processing/ale_tsv_output/11.Thyroid_US_Images.tsv',
    '39': '/media/ps/data-ssd/json_processing/ale_tsv_output/39_translated.tsv',
    # '44': '/media/ps/data-ssd/json_processing/ale_tsv_output/44.COVID-BLUES-frames.tsv',
}

# 单例模型缓存
class BertModelCache:
    _instance = None

    def __init__(self):
        if self._instance is not None:
            raise Exception("单例模式，请使用 instance() 方法")
            
        self.tokenizer, self.model, self.device = self.load_bert_model()
        BertModelCache._instance = self

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = BertModelCache()
        return cls._instance

    def load_bert_model(self):
        """优化后的模型加载方法"""
        try:
            if HAVE_LOCAL_BERTSCORE_MODEL:
                model_path = f"{LOCAL_MODEL_DIR}/{BERTSCORE_MODEL_NAME}"
                tokenizer = AutoTokenizer.from_pretrained(model_path)
                model = AutoModel.from_pretrained(model_path)
            else:
                tokenizer = AutoTokenizer.from_pretrained("bert-base-multilingual-cased")
                model = AutoModel.from_pretrained("bert-base-multilingual-cased")

            device = "cuda" if torch.cuda.is_available() else "cpu"
            model = model.to(device)
            return tokenizer, model, device
        except Exception as e:
            print(f"模型加载失败: {str(e)}")
            return None, None, "cpu"

    @classmethod
    def clear_cache(cls):
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

def batch_bertscore(refs_dict, hyps_dict):
    """批量计算BERTScore"""
    cache = BertModelCache.instance()
    scores = {}
    
    try:
        import bert_score
        calc_params = {
            "model_type": "bert-base-multilingual-cased",
            "lang": "en",
            "device": cache.device,
            "batch_size": 8  
        }

        # 构建输入列表
        all_hyp, all_ref = [], []
        for case_id, hyp in hyps_dict.items():
            ref = refs_dict.get(case_id, [])
            if ref:
                all_hyp.extend(hyp)
                all_ref.extend(ref)

        # 批量计算
        if len(all_hyp) > 0:
            _, _, F1 = bert_score.score(
                all_hyp, all_ref,
                **calc_params
            )
            
            # 按案例聚合分数
            idx = 0
            for case_id, hyp in hyps_dict.items():
                refs = refs_dict.get(case_id, [])
                if refs:
                    scores[case_id] = F1[idx:idx+len(refs)].mean().item()
                    idx += len(refs)
    except Exception as e:
        print(f"BERTScore批量计算失败: {str(e)}")
    finally:
        BertModelCache.clear_cache()
    
    return scores

class MedicalReportScorer:
    def __init__(self, refs, hyps):
        self.refs = refs
        self.hyps = hyps
        self.scorers = [
            (Bleu(4), 'Bleu'),
            (Rouge(), 'Rouge')
        ]

    def evaluate(self):
        metrics = {}
        for scorer, name in self.scorers:
            try:
                score, scores = scorer.compute_score(self.refs, self.hyps)
                if name == 'Bleu':
                    for i, v in enumerate(score):
                        metrics[f'Bleu-{i+1}'] = v * 100
                    # 打印BLEU分数详情
                    print(f"\nBLEU分数详情:")
                    print(f"BLEU-1: {score[0]*100:.4f}")
                    print(f"BLEU-2: {score[1]*100:.4f}")
                    print(f"BLEU-3: {score[2]*100:.4f}")
                    print(f"BLEU-4: {score[3]*100:.4f}")
                    
                    # 检查是否所有分数都为零
                    if all(v == 0 for v in score):
                        print("警告: 所有BLEU分数均为零，可能存在以下问题:")
                        print("1. 参考标签与生成标签格式不匹配")
                        print("2. 数据对齐问题")
                        print("3. 词汇重叠度过低")
                        
                        # 打印一些样本的详细分数
                        print("\n单个样本BLEU分数:")
                        sample_ids = list(self.refs.keys())[:5]  # 取前5个样本
                        for id in sample_ids:
                            print(f"ID: {id}")
                            print(f"参考: {self.refs[id][0][:100]}...")
                            print(f"生成: {self.hyps[id][0][:100]}...")
                            print(f"分数: {scores[id][0]*100:.4f}\n")
                else:
                    metrics[name] = score * 100
            except Exception as e:
                print(f"{name}计算失败: {str(e)}")

        # BERTScore
        try:
            bert_scores = batch_bertscore(self.refs, self.hyps)
            metrics['BERTScore'] = np.mean(list(bert_scores.values())) * 100
        except Exception as e:
            print(f"BERTScore计算失败: {str(e)}")
            metrics['BERTScore'] = 0.0

        return metrics
    
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
    """读取JSONL文件并合并TSV中的参考报告"""
    # 读取生成报告
    with open(jsonl_path, 'r') as f:
        jsonl_data = [json.loads(line) for line in f]
    df_jsonl = pd.DataFrame(jsonl_data)

    df_tsv = pd.read_csv(tsv_path, sep='\t')
    
    # 打印调试信息
    print(f"JSONL文件行数: {len(df_jsonl)}")
    print(f"TSV文件行数: {len(df_tsv)}")
    
    # 检查两个文件的长度是否一致
    if len(df_jsonl) != len(df_tsv):
        print(f"警告：JSONL文件({len(df_jsonl)}行)和TSV文件({len(df_tsv)}行)行数不匹配!")
        # 如果不一致，只使用最小长度的部分
        min_len = min(len(df_jsonl), len(df_tsv))
        df_jsonl = df_jsonl.iloc[:min_len]
        df_tsv = df_tsv.iloc[:min_len]
        print(f"已调整为使用前{min_len}行进行评估")
    
    # 打印前5条记录的ID和内容进行对比
    print("\n前5条记录对比:")
    for i in range(min(5, len(df_jsonl))):
        print(f"ID: {df_jsonl.iloc[i]['id']}")
        print(f"生成: {df_jsonl.iloc[i]['response'][:100]}...")
        print(f"参考: {df_tsv.iloc[i]['caption'][:100]}...\n")
    
    df_merged = df_jsonl.assign(cap_ans=df_tsv['caption'])
    return df_merged

def model_eval(data, jsonl_path=None):
    """评估函数，增强对不同格式回复的处理能力"""
    # 从文件路径中提取模型名称
    model_name = os.path.basename(os.path.dirname(jsonl_path)) if jsonl_path else None
    
    # 初始化参考和生成文本字典
    refs = {}
    hyps = {}
    
    # 处理每一行数据
    for i, row in data.iterrows():
        # 检查是否有 'model' 字段，如果没有，使用从路径中提取的模型名称
        if 'model' in data.columns and len(data['model']) > 0:
            current_model = data['model'][0]
        else:
            current_model = model_name
            
        # 获取参考文本和生成文本
        ref = row['cap_ans']
        hyp = row['response']
        
        # 清理生成文本：去除首尾空格
        if hyp is not None:
            hyp = hyp.strip()
        else:
            hyp = ""
            
        # 清理参考文本（如果是字符串）
        if isinstance(ref, str):
            ref = ref.strip()
        elif ref is None:
            ref = ""
        
        # 将文本添加到字典中
        refs[str(i)] = [ref]
        hyps[str(i)] = [hyp]
        
        # 打印对比示例（前5个）
        if i < 5:
            print(f"ID: {i}")
            print(f"生成: {hyp[:100]}...")
            print(f"参考: {ref[:100]}...\n")
        # 计算单个样本的BLEU-1分数
        from pycocoevalcap.bleu.bleu import Bleu
        bleu_scorer = Bleu(4)
        sample_score, _ = bleu_scorer.compute_score({str(i): refs[str(i)]}, {str(i): hyps[str(i)]})
        print(f"单样本BLEU-1分数: {sample_score[0]*100:.4f}\n")

    scorer = MedicalReportScorer(refs, hyps)
    metrics = scorer.evaluate()
    
    print(f"总体评估结果: {metrics}")
    return metrics
    # except Exception as e:
    #     return {'error': f"Evaluation failed: {str(e)}"}}

def batch_evaluate_all_tasks():
    base_dir = '/home/guohongcheng/DolphinV1.9p/report'
    output_file = '/home/guohongcheng/DolphinV1.9p_results/report_results.txt'
    
    all_results = []
    
    for task_id in TSV_PATH:
        task_pairs = find_model_files(base_dir, task_id)
        if not task_pairs:
            print(f"Task {task_id} skipped: no files found")
            continue
        
        for jsonl_path, tsv_path in task_pairs:
            # try:
            # 读取数据
            data = read_jsonl_with_tsv(jsonl_path, tsv_path)
            if data.empty:
                print(f"Skipped {jsonl_path}: empty data")
                continue
            
            # 从路径解析模型名称
            model_name = os.path.basename(os.path.dirname(jsonl_path))
            
            # 执行评估
            metrics = model_eval(data, jsonl_path=jsonl_path)
            
            if 'error' in metrics:
                print(f"Skipped {model_name}@{task_id}: {metrics['error']}")
                continue
            
            # 记录结果
            all_results.append({
                'task_id': task_id,
                'model': model_name,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
    columns = [
        'task_id', 'model', 'timestamp',
        'Bleu-1', 'Bleu-2', 'Bleu-3', 'Bleu-4',
        'Rouge', 'BERTScore'
    ]
    
    with open(output_file, 'w') as f:
        # 写入表头
        f.write('\t'.join(columns) + '\n')
        
        # 写入数据行
        for result in results:
            row = [
                result['task_id'],
                result['model'],
                result['timestamp'],
                f"{result.get('Bleu-1', 0):.4f}",
                f"{result.get('Bleu-2', 0):.4f}",
                f"{result.get('Bleu-3', 0):.4f}",
                f"{result.get('Bleu-4', 0):.4f}",
                f"{result.get('Rouge', 0):.4f}",
                f"{result.get('BERTScore', 0):.4f}"
            ]
            f.write('\t'.join(row) + '\n')

if __name__ == "__main__":
    batch_evaluate_all_tasks()
