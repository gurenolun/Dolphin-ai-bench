#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive PNG Chart Generator for Segmentation Task Performance (Standard Mode)
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
            "04",
            "09",
            "13",
            "16",
            "17",
            "18",
            "23",
            "31",
            "32",
            "37",
            "38",
            "47",
            "48",
            "49",
            "50",
            "52",
            "53",
            "64",
            "67"
        ],
        "v1_values": [
            0.37,
            0.35,
            0.2451,
            0.64,
            0.44,
            0.4314,
            0.48,
            0.505,
            0.2913,
            0.595,
            0.88,
            0.3073,
            0.362,
            0.3855,
            0.5673,
            0.9,
            0.396,
            0.4,
            0.51
        ],
        "v2_values": [
            0.4,
            0.43,
            0.0784,
            0.58,
            0.22,
            0.2255,
            0.45,
            0.5446,
            0.0971,
            0.4352,
            0.67,
            0.3687,
            0.124,
            0.4277,
            0.2019,
            0.54,
            0.3069,
            0.32,
            0.32
        ],
        "metric_name": "Accuracy"
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
    title_text = "Segmentation Task Performance (Standard Mode)"
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
    output_file = "segmentation_standard_mode_comprehensive_comparison.png"
    img.save(output_file)
    print(f"Comprehensive PNG chart saved to: {output_file}")
    return True

if __name__ == "__main__":
    success = create_comprehensive_png_chart()
    if not success:
        print("Failed to create comprehensive PNG chart")
