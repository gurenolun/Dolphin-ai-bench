#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import argparse
from datetime import datetime
import base64
from typing import List, Dict, Tuple

import pandas as pd
from PIL import Image
import io


def image_to_base64(image_path: str, max_size: Tuple[int, int] = (800, 600)) -> str:
    try:
        if not image_path or not os.path.exists(image_path):
            return None
        with Image.open(image_path) as img:
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            buffer.seek(0)
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception:
        return None


def find_first_jsonl(base_dir: str, task_type: str, task_id: str) -> str:
    task_dir = os.path.join(base_dir, task_type, task_id)
    if not os.path.exists(task_dir):
        return None
    for root, _, files in os.walk(task_dir):
        for f in files:
            if f.endswith('.jsonl'):
                return os.path.join(root, f)
    return None


def read_jsonl(path: str) -> pd.DataFrame:
    with open(path, 'r', encoding='utf-8') as f:
        rows = [json.loads(line.strip()) for line in f]
    return pd.DataFrame(rows)


def read_reference_tsv(tsv_root: str, task_type: str, task_id: str) -> pd.DataFrame:
    # 允许灵活组织：默认 data/tsv/<task_type>/<task_id>.tsv 或 data/tsv/<task_id>.tsv
    candidates = [
        os.path.join(tsv_root, task_type, f"{task_id}.tsv"),
        os.path.join(tsv_root, f"{task_id}.tsv"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return pd.read_csv(p, sep='\t')
    return None


def convert_seg_reference_to_location(val):
    # 允许 val 是 json 字符串或结构
    import math
    try:
        if isinstance(val, str):
            try:
                data = json.loads(val.replace("'", '"'))
            except Exception:
                return 'not visible'
        else:
            data = val

        if isinstance(data, dict):
            coords = list(data.values())[0]
        elif isinstance(data, list):
            coords = list(data[0].values())[0] if data and isinstance(data[0], dict) else data
        else:
            coords = data

        if not isinstance(coords, (list, tuple)) or len(coords) < 2:
            return 'not visible'
        cx, cy = float(coords[0]), float(coords[1])
        if math.isnan(cx) or math.isnan(cy):
            return 'not visible'
        low, high = 0.45, 0.55
        y_pos = 'upper' if cy < low else ('middle' if cy < high else 'lower')
        x_pos = 'left' if cx < low else ('center' if cx < high else 'right')
        return 'center' if (y_pos == 'middle' and x_pos == 'center') else f"{y_pos} {x_pos}"
    except Exception:
        return 'not visible'


def merge_with_reference(df_jsonl: pd.DataFrame, df_tsv: pd.DataFrame, task_type: str) -> pd.DataFrame:
    if df_tsv is None or df_tsv.empty:
        df_jsonl['reference_answer'] = ''
        return df_jsonl

    if task_type == 'cla':
        if 'classes' in df_tsv.columns:
            df_jsonl['reference_answer'] = df_tsv['classes']
        elif 'class' in df_tsv.columns:
            df_jsonl['reference_answer'] = df_tsv['class']
        else:
            df_jsonl['reference_answer'] = ''
    elif task_type == 'seg':
        if 'keypoints' in df_tsv.columns:
            df_jsonl['reference_answer'] = df_tsv['keypoints'].apply(convert_seg_reference_to_location)
        elif 'gt_bbox' in df_tsv.columns:
            df_jsonl['reference_answer'] = df_tsv['gt_bbox'].apply(convert_seg_reference_to_location)
        elif 'seg_ans' in df_tsv.columns:
            df_jsonl['reference_answer'] = df_tsv['seg_ans'].apply(convert_seg_reference_to_location)
        else:
            df_jsonl['reference_answer'] = ''
    else:  # report
        if 'caption' in df_tsv.columns:
            df_jsonl['reference_answer'] = df_tsv['caption']
        else:
            df_jsonl['reference_answer'] = ''
    return df_jsonl


def extract_model_response(text: str) -> str:
    if text is None:
        return ''
    t = text.strip()
    # 若含深度思考标签，取末段
    if '</think>' in t:
        parts = t.split('</think>')
        if len(parts) > 1:
            t = parts[-1].strip()
    return t


def build_tasks(default: bool = True) -> List[Dict[str, str]]:
    if not default:
        return []
    # 默认匿名化三案例（可通过 --task 重复传参自定义）
    return [
        {'type': 'cla', 'id': 'task_A', 'index': '0', 'desc': 'Task A'},
        {'type': 'seg', 'id': 'task_B', 'index': '0', 'desc': 'Task B'},
        {'type': 'report', 'id': 'task_C', 'index': '0', 'desc': 'Task C'},
    ]


def parse_task_arg(task_arg: str) -> Dict[str, str]:
    # 形如: cla:03:2:Task A
    parts = task_arg.split(':')
    if len(parts) < 4:
        raise ValueError("--task 参数格式应为 type:id:index:desc，例如 cla:03:2:Task A")
    return {'type': parts[0], 'id': parts[1], 'index': parts[2], 'desc': ':'.join(parts[3:])}


def main():
    parser = argparse.ArgumentParser(description='三案例对比报告（匿名化版本）')
    parser.add_argument('--standard-dir', type=str, default='data/models/Standard', help='标准模式结果根目录')
    parser.add_argument('--deep-dir', type=str, default='data/models/Deep', help='深度推理模式结果根目录')
    parser.add_argument('--tsv-root', type=str, default='data/tsv', help='参考TSV根目录')
    parser.add_argument('--output', type=str, default='Three_Case_Comparison_Report.md', help='输出报告路径')
    parser.add_argument('--task', action='append', help='任务定义 type:id:index:desc，可多次传入')
    args = parser.parse_args()

    tasks = []
    if args.task:
        for t in args.task:
            tasks.append(parse_task_arg(t))
    else:
        tasks = build_tasks(default=True)

    lines: List[str] = []
    lines.append("# Three-Case Comparison Report (Anonymized)")
    lines.append("")
    lines.append(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    for idx, task in enumerate(tasks, 1):
        task_type = task['type']
        task_id = task['id']
        sample_index = int(task['index'])
        desc = task['desc']

        lines.append(f"## Case {idx}: {desc}")
        lines.append("")

        std_jsonl = find_first_jsonl(args.standard_dir, task_type, task_id)
        deep_jsonl = find_first_jsonl(args.deep_dir, task_type, task_id)
        tsv_df = read_reference_tsv(args.tsv_root, task_type, task_id)

        # 读取与合并
        std_df = read_jsonl(std_jsonl) if std_jsonl else None
        deep_df = read_jsonl(deep_jsonl) if deep_jsonl else None
        if std_df is not None:
            std_df = merge_with_reference(std_df, tsv_df, task_type)
        if deep_df is not None:
            deep_df = merge_with_reference(deep_df, tsv_df, task_type)

        # 提取样本
        if std_df is not None and len(std_df) > sample_index:
            s = std_df.iloc[sample_index]
            # 图片路径尝试
            images = s.get('images', []) if isinstance(s.get('images', []), list) else []
            img_path = images[0] if images else s.get('image', '')
            ref = s.get('reference_answer', '')
            std_resp = extract_model_response(s.get('response', ''))
        else:
            img_path, ref, std_resp = '', '', ''

        if deep_df is not None and len(deep_df) > sample_index:
            d = deep_df.iloc[sample_index]
            deep_resp = extract_model_response(d.get('response', ''))
        else:
            deep_resp = ''

        # 信息写入
        lines.append(f"- Task Type: {task_type}")
        lines.append(f"- Image Path: `{img_path or 'N/A'}`")
        lines.append("")

        # 尝试嵌入图片
        if img_path:
            # 尝试多种根路径：相对/原样
            candidate_paths = [
                img_path,
                os.path.join('data/images', img_path) if not os.path.isabs(img_path) else img_path,
            ]
            embedded = False
            for p in candidate_paths:
                b64 = image_to_base64(p)
                if b64:
                    lines.append(f"![image](data:image/jpeg;base64,{b64})")
                    lines.append("")
                    embedded = True
                    break
            if not embedded:
                lines.append("(Image preview unavailable)")
                lines.append("")

        lines.append(f"**Reference**: {str(ref)[:200] if ref else 'N/A'}")
        lines.append("")
        lines.append("### Responses")
        lines.append("")
        lines.append("- Standard:")
        lines.append("```")
        lines.append(std_resp)
        lines.append("```")
        lines.append("")
        lines.append("- Deep:")
        lines.append("```")
        lines.append(deep_resp)
        lines.append("```")
        lines.append("")
        lines.append("---\n")

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"Report saved to: {args.output}")


if __name__ == '__main__':
    main()

