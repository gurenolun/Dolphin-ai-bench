#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive PNG Chart Generator for Classification Task Performance (Standard Mode)
This script creates subplots for all metrics in one chart
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL not available, will create text-based chart")

import os
import math

def create_comprehensive_png_chart():
    """Create comprehensive PNG chart with subplots for all metrics"""
    
    if not PIL_AVAILABLE:
        print("PIL (Pillow) not available. Please install with: pip install Pillow")
        return False
    
    # Chart data
    metrics_data = {
    "acc": {
        "task_labels": [
            "03",
            "10",
            "18",
            "21",
            "23",
            "25",
            "28",
            "28_class",
            "32",
            "37",
            "40",
            "42",
            "44",
            "50",
            "53",
            "57",
            "66",
            "69",
            "70",
            "74is_normal",
            "74is_visible",
            "75",
            "anatomy"
        ],
        "v1_values": [
            0.9416,
            0.9868,
            0.9314,
            0.6725,
            0.82,
            0.69,
            0.1923,
            1.0,
            0.6019,
            0.9609,
            0.4587,
            0.4356,
            0.3426,
            0.3725,
            0.6238,
            0.4811,
            0.89,
            0.63,
            0.71,
            0.7431,
            0.6972,
            0.99,
            0.5636
        ],
        "v2_values": [
            0.7956,
            0.9474,
            0.8824,
            0.7661,
            0.79,
            0.69,
            0.1923,
            0.9821,
            0.5631,
            0.9059,
            0.3945,
            0.6337,
            0.3333,
            0.3431,
            0.6238,
            0.6415,
            0.82,
            0.49,
            0.7,
            0.7156,
            0.7706,
            0.99,
            0.5545
        ],
        "metric_name": "Accuracy"
    },
    "precision": {
        "task_labels": [
            "03",
            "10",
            "18",
            "21",
            "23",
            "25",
            "28",
            "28_class",
            "32",
            "37",
            "40",
            "42",
            "44",
            "50",
            "53",
            "57",
            "66",
            "69",
            "70",
            "74is_normal",
            "74is_visible",
            "75",
            "anatomy"
        ],
        "v1_values": [
            0.9074,
            0.9878,
            0.9329,
            0.7135,
            0.838,
            0.6775,
            0.2236,
            1.0,
            0.2603,
            0.967,
            0.2118,
            0.5352,
            0.2988,
            0.5491,
            0.2117,
            0.4395,
            0.8881,
            0.7103,
            0.592,
            0.6778,
            0.4919,
            0.9902,
            0.325
        ],
        "v2_values": [
            0.7429,
            0.9453,
            0.8976,
            0.7683,
            0.8175,
            0.6775,
            0.0333,
            0.875,
            0.5692,
            0.2585,
            0.1471,
            0.2997,
            0.2293,
            0.2798,
            0.197,
            0.3208,
            0.8062,
            0.1472,
            0.6351,
            0.4286,
            0.503,
            0.9902,
            0.4058
        ],
        "metric_name": "Precision"
    },
    "recall": {
        "task_labels": [
            "03",
            "10",
            "18",
            "21",
            "23",
            "25",
            "28",
            "28_class",
            "32",
            "37",
            "40",
            "42",
            "44",
            "50",
            "53",
            "57",
            "66",
            "69",
            "70",
            "74is_normal",
            "74is_visible",
            "75",
            "anatomy"
        ],
        "v1_values": [
            0.9602,
            0.9854,
            0.9314,
            0.6657,
            0.7714,
            0.6995,
            0.1667,
            1.0,
            0.2387,
            0.9609,
            0.1933,
            0.5244,
            0.2848,
            0.2794,
            0.204,
            0.4389,
            0.8737,
            0.5651,
            0.5773,
            0.6359,
            0.4883,
            0.99,
            0.2881
        ],
        "v2_values": [
            0.8236,
            0.9432,
            0.8824,
            0.7645,
            0.7441,
            0.6995,
            0.1667,
            0.8594,
            0.5419,
            0.2464,
            0.1358,
            0.2647,
            0.2397,
            0.2574,
            0.1878,
            0.5,
            0.8125,
            0.1356,
            0.6943,
            0.3787,
            0.5028,
            0.99,
            0.4917
        ],
        "metric_name": "Recall"
    },
    "f1": {
        "task_labels": [
            "03",
            "10",
            "18",
            "21",
            "23",
            "25",
            "28",
            "28_class",
            "32",
            "37",
            "40",
            "42",
            "44",
            "50",
            "53",
            "57",
            "66",
            "69",
            "70",
            "74is_normal",
            "74is_visible",
            "75",
            "anatomy"
        ],
        "v1_values": [
            0.9283,
            0.9864,
            0.9313,
            0.6504,
            0.7925,
            0.6757,
            0.1342,
            1.0,
            0.2483,
            0.9625,
            0.1994,
            0.4211,
            0.282,
            0.2821,
            0.2049,
            0.4392,
            0.8799,
            0.5793,
            0.5759,
            0.6464,
            0.4847,
            0.99,
            0.2969
        ],
        "v2_values": [
            0.7521,
            0.9441,
            0.8812,
            0.7647,
            0.7686,
            0.6757,
            0.0556,
            0.8667,
            0.5023,
            0.252,
            0.1396,
            0.2584,
            0.2302,
            0.23,
            0.1914,
            0.3908,
            0.809,
            0.1325,
            0.6432,
            0.3797,
            0.5028,
            0.99,
            0.4177
        ],
        "metric_name": "F1-Score"
    }
}
    
    num_metrics = len(metrics_data)
    if num_metrics == 0:
        print("No data to chart")
        return False
    
    # Calculate subplot layout
    if num_metrics == 1:
        rows, cols = 1, 1
    elif num_metrics <= 2:
        rows, cols = 1, 2
    elif num_metrics <= 4:
        rows, cols = 2, 2
    elif num_metrics <= 6:
        rows, cols = 2, 3
    else:
        rows, cols = 3, 3
    
    # Image settings - adjusted for better title display
    subplot_width, subplot_height = 600, 400
    margin = 60
    title_height = 100  # Increased for better title space
    width = cols * subplot_width + (cols + 1) * margin
    height = rows * subplot_height + (rows + 1) * margin + title_height
    
    bg_color = (255, 255, 255)  # White background
    
    # Create image
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to load fonts
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)  # Reduced size
        subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)  # Reduced size
        label_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
    except:
        try:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            label_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        except:
            print("Could not load fonts")
            title_font = subtitle_font = label_font = small_font = None
    
    # Colors
    v1_color = (46, 134, 171)    # Blue for Model 1
    v2_color = (162, 59, 114)    # Purple for Model 2
    text_color = (51, 51, 51)     # Dark gray for text
    grid_color = (200, 200, 200)  # Light gray for grid
    
    # Main title - adjusted for better fit
    title_text = "Classification Task Performance (Standard Mode)"
    if title_font:
        # Split long titles into multiple lines
        if len(title_text) > 50:
            words = title_text.split()
            lines = []
            current_line = []
            for word in words:
                current_line.append(word)
                if len(' '.join(current_line)) > 40:
                    if len(current_line) > 1:
                        current_line.pop()
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(' '.join(current_line))
                        current_line = []
            if current_line:
                lines.append(' '.join(current_line))
            
            for i, line in enumerate(lines):
                title_bbox = draw.textbbox((0, 0), line, font=title_font)
                title_width = title_bbox[2] - title_bbox[0]
                title_x = (width - title_width) // 2
                draw.text((title_x, 15 + i * 30), line, fill=text_color, font=title_font)
        else:
            title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (width - title_width) // 2
            draw.text((title_x, 25), title_text, fill=text_color, font=title_font)
    
    # Draw subplots
    metric_idx = 0
    for row in range(rows):
        for col in range(cols):
            if metric_idx >= num_metrics:
                break
                
            metric = list(metrics_data.keys())[metric_idx]
            data = metrics_data[metric]
            
            task_labels = data['task_labels']
            v1_values = data['v1_values']
            v2_values = data['v2_values']
            metric_name = data['metric_name']
            
            # Calculate subplot position
            subplot_x = margin + col * (subplot_width + margin)
            subplot_y = title_height + margin + row * (subplot_height + margin)
            
            # Subplot area
            chart_left = subplot_x + 60
            chart_right = subplot_x + subplot_width - 20
            chart_top = subplot_y + 40
            chart_bottom = subplot_y + subplot_height - 60
            chart_width = chart_right - chart_left
            chart_height = chart_bottom - chart_top
            
            # Subplot title - truncate if too long
            display_title = metric_name
            if len(display_title) > 25:
                display_title = display_title[:22] + "..."
            
            if subtitle_font:
                subtitle_bbox = draw.textbbox((0, 0), display_title, font=subtitle_font)
                subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
                subtitle_x = subplot_x + (subplot_width - subtitle_width) // 2
                draw.text((subtitle_x, subplot_y + 5), display_title, fill=text_color, font=subtitle_font)
            
            # Find max value for this subplot
            max_value = max(max(v1_values) if v1_values else [0], max(v2_values) if v2_values else [0])
            if max_value == 0:
                max_value = 1
            
            # Draw grid lines
            for i in range(6):
                y = chart_bottom - (i * chart_height // 5)
                draw.line([(chart_left, y), (chart_right, y)], fill=grid_color, width=1)
                
                # Y-axis labels
                value = (i * max_value) / 5
                if small_font:
                    draw.text((chart_left - 50, y - 6), f"{value:.2f}", fill=text_color, font=small_font)
            
            # Calculate bar dimensions
            num_tasks = len(task_labels)
            if num_tasks > 0:
                bar_group_width = chart_width // num_tasks
                bar_width = max(8, bar_group_width // 3)
                bar_spacing = max(2, bar_width // 4)
                
                # Draw bars
                for i, (task_id, v1_val, v2_val) in enumerate(zip(task_labels, v1_values, v2_values)):
                    # Calculate positions
                    group_center = chart_left + (i + 0.5) * bar_group_width
                    
                    v1_bar_left = int(group_center - bar_width - bar_spacing//2)
                    v2_bar_left = int(group_center + bar_spacing//2)
                    
                    # Calculate heights
                    v1_height = int((v1_val / max_value) * chart_height)
                    v2_height = int((v2_val / max_value) * chart_height)
                    
                    # Draw bars
                    v1_bar_top = chart_bottom - v1_height
                    v2_bar_top = chart_bottom - v2_height
                    
                    # Model 1 bar
                    draw.rectangle([v1_bar_left, v1_bar_top, v1_bar_left + bar_width, chart_bottom], 
                                  fill=v1_color, outline=v1_color)
                    
                    # Model 2 bar
                    draw.rectangle([v2_bar_left, v2_bar_top, v2_bar_left + bar_width, chart_bottom], 
                                  fill=v2_color, outline=v2_color)
                    
                    # Task label (show all labels, rotate if needed)
                    if small_font:
                        label_x = group_center - len(task_id) * 2
                        draw.text((label_x, chart_bottom + 5), task_id, fill=text_color, font=small_font)
            
            # Y-axis label for this subplot
            if label_font:
                y_label = metric_name[:15] + "..." if len(metric_name) > 15 else metric_name
                draw.text((subplot_x + 5, chart_top + chart_height//2), y_label, fill=text_color, font=label_font)
            
            metric_idx += 1
    
    # Global legend
    legend_y = height - 40
    legend_x = margin
    
    # Model 1 legend
    draw.rectangle([legend_x, legend_y, legend_x + 20, legend_y + 15], fill=v1_color)
    if label_font:
        draw.text((legend_x + 30, legend_y), "Dolphin-1.6", fill=text_color, font=label_font)
    
    # Model 2 legend
    legend_x += 150
    draw.rectangle([legend_x, legend_y, legend_x + 20, legend_y + 15], fill=v2_color)
    if label_font:
        draw.text((legend_x + 30, legend_y), "Dolphin-1.9", fill=text_color, font=label_font)
    
    # Save image
    output_file = "classification_standard_mode_comprehensive_comparison.png"
    img.save(output_file)
    print(f"Comprehensive PNG chart saved to: {output_file}")
    return True

if __name__ == "__main__":
    success = create_comprehensive_png_chart()
    if not success:
        print("Failed to create comprehensive PNG chart")
