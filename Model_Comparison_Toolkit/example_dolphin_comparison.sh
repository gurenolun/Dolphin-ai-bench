#!/bin/bash
# Dolphin 1.6 vs 1.9 Comparison Example Script

echo "=== Dolphin Model Comparison Example ==="
echo "This script demonstrates how to use the Model Comparison Toolkit"
echo "to compare Dolphin 1.6 and 1.9 versions"
echo ""

# Check if the toolkit exists
if [ ! -f "model_comparison_toolkit.py" ]; then
    echo "Error: model_comparison_toolkit.py not found in current directory"
    echo "Please run this script from the Model_Comparison_Toolkit directory"
    exit 1
fi

# Set paths (modify these according to your setup)
DOLPHIN16_STANDARD="/path/to/DolphinV1.6r_results"
DOLPHIN16_DEEP="/path/to/DolphinV1.6rd_results"
DOLPHIN19_STANDARD="/path/to/DolphinV1.9p_results"
DOLPHIN19_DEEP="/path/to/DolphinV1.9_results"

echo "Data paths:"
echo "  Dolphin 1.6 Standard: $DOLPHIN16_STANDARD"
echo "  Dolphin 1.6 Deep:     $DOLPHIN16_DEEP"
echo "  Dolphin 1.9 Standard: $DOLPHIN19_STANDARD"
echo "  Dolphin 1.9 Deep:     $DOLPHIN19_DEEP"
echo ""

# Check if directories exist
missing_dirs=()
for dir in "$DOLPHIN16_STANDARD" "$DOLPHIN16_DEEP" "$DOLPHIN19_STANDARD" "$DOLPHIN19_DEEP"; do
    if [ ! -d "$dir" ]; then
        missing_dirs+=("$dir")
    fi
done

if [ ${#missing_dirs[@]} -gt 0 ]; then
    echo "Warning: The following directories do not exist:"
    for dir in "${missing_dirs[@]}"; do
        echo "  - $dir"
    done
    echo ""
    echo "Please update the paths in this script or create the directories"
    echo "You can still run with --include-deep flag removed if deep reasoning data is missing"
    echo ""
fi

# Option 1: Full comparison with both standard and deep reasoning modes
echo "Option 1: Full comparison (Standard + Deep Reasoning)"
echo "Command:"
echo "python3 model_comparison_toolkit.py \\"
echo "    --model1-name \"Dolphin-1.6\" \\"
echo "    --model2-name \"Dolphin-1.9\" \\"
echo "    --model1-standard-dir \"$DOLPHIN16_STANDARD\" \\"
echo "    --model2-standard-dir \"$DOLPHIN19_STANDARD\" \\"
echo "    --model1-deep-dir \"$DOLPHIN16_DEEP\" \\"
echo "    --model2-deep-dir \"$DOLPHIN19_DEEP\" \\"
echo "    --include-deep \\"
echo "    --output-dir \"Dolphin_1.6_vs_1.9_Full_Analysis\""
echo ""

# Option 2: Standard mode only
echo "Option 2: Standard mode only"
echo "Command:"
echo "python3 model_comparison_toolkit.py \\"
echo "    --model1-name \"Dolphin-1.6\" \\"
echo "    --model2-name \"Dolphin-1.9\" \\"
echo "    --model1-standard-dir \"$DOLPHIN16_STANDARD\" \\"
echo "    --model2-standard-dir \"$DOLPHIN19_STANDARD\" \\"
echo "    --output-dir \"Dolphin_1.6_vs_1.9_Standard_Only\""
echo ""

# Ask user which option to run
echo "Which option would you like to run?"
echo "1) Full comparison (Standard + Deep Reasoning)"
echo "2) Standard mode only"
echo "3) Just show commands (don't run)"
echo "4) Exit"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "Running full comparison..."
        python3 model_comparison_toolkit.py \
            --model1-name "Dolphin-1.6" \
            --model2-name "Dolphin-1.9" \
            --model1-standard-dir "$DOLPHIN16_STANDARD" \
            --model2-standard-dir "$DOLPHIN19_STANDARD" \
            --model1-deep-dir "$DOLPHIN16_DEEP" \
            --model2-deep-dir "$DOLPHIN19_DEEP" \
            --include-deep \
            --output-dir "Dolphin_1.6_vs_1.9_Full_Analysis"
        ;;
    2)
        echo ""
        echo "Running standard mode comparison..."
        python3 model_comparison_toolkit.py \
            --model1-name "Dolphin-1.6" \
            --model2-name "Dolphin-1.9" \
            --model1-standard-dir "$DOLPHIN16_STANDARD" \
            --model2-standard-dir "$DOLPHIN19_STANDARD" \
            --output-dir "Dolphin_1.6_vs_1.9_Standard_Only"
        ;;
    3)
        echo "Commands displayed above. You can copy and modify them as needed."
        ;;
    4)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice. Exiting..."
        exit 1
        ;;
esac

echo ""
echo "=== Example completed ==="
echo ""
echo "Next steps:"
echo "1. Navigate to the generated output directory"
echo "2. Run './generate_all_charts.sh' to create PNG charts"
echo "3. Check the 'charts/' directory for generated images"
echo "4. Review the 'reports/' directory for detailed analysis"
echo ""
echo "For other model comparisons, modify the paths and model names in this script"
echo "or use the toolkit directly with your own parameters." 