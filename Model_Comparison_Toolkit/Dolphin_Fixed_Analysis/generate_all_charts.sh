#!/bin/bash
# Comprehensive PNG Generator for Model Comparison

echo "=== Generating Comprehensive Model Comparison Charts ==="
echo "Comparing Dolphin-1.6 vs Dolphin-1.9"
echo "Output directory: Dolphin_Fixed_Analysis"

cd "Dolphin_Fixed_Analysis/scripts"

# Check if PIL is available
python3 -c "from PIL import Image; print('PIL available')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "PIL (Pillow) is available, generating comprehensive PNG charts..."
    
    # Run all comprehensive PNG generators
    echo "Generating classification_standard_mode_comprehensive_png_generator.py..."
    python3 classification_standard_mode_comprehensive_png_generator.py
    mv *.png ../charts/
    echo "Generating measurement_standard_mode_comprehensive_png_generator.py..."
    python3 measurement_standard_mode_comprehensive_png_generator.py
    mv *.png ../charts/
    echo "Generating segmentation_standard_mode_comprehensive_png_generator.py..."
    python3 segmentation_standard_mode_comprehensive_png_generator.py
    mv *.png ../charts/
    echo "Generating report_standard_mode_comprehensive_png_generator.py..."
    python3 report_standard_mode_comprehensive_png_generator.py
    mv *.png ../charts/
    echo "Generating classification_deep_reasoning_mode_comprehensive_png_generator.py..."
    python3 classification_deep_reasoning_mode_comprehensive_png_generator.py
    mv *.png ../charts/
    echo "Generating measurement_deep_reasoning_mode_comprehensive_png_generator.py..."
    python3 measurement_deep_reasoning_mode_comprehensive_png_generator.py
    mv *.png ../charts/
    echo "Generating segmentation_deep_reasoning_mode_comprehensive_png_generator.py..."
    python3 segmentation_deep_reasoning_mode_comprehensive_png_generator.py
    mv *.png ../charts/
    echo "Generating report_deep_reasoning_mode_comprehensive_png_generator.py..."
    python3 report_deep_reasoning_mode_comprehensive_png_generator.py
    mv *.png ../charts/

    echo "All comprehensive charts generated!"
    echo "Generated $(ls -1 ../charts/*.png 2>/dev/null | wc -l) PNG files"
    ls -la ../charts/*.png 2>/dev/null
else
    echo "PIL (Pillow) not available. Please install with:"
    echo "pip install Pillow"
fi

echo "Done!"
