#!/bin/bash
set -e

# Start Xvfb for headless GUI operations
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99

# Wait for Xvfb to be ready
sleep 2

case "$1" in
    slice)
        shift
        MODEL=""
        PROFILE=""
        
        while [[ $# -gt 0 ]]; do
            case $1 in
                --model)
                    MODEL="$2"
                    shift 2
                    ;;
                --printer-profile)
                    PROFILE="$2"
                    shift 2
                    ;;
                *)
                    echo "Unknown option: $1"
                    exit 1
                    ;;
            esac
        done
        
        if [[ -z "$MODEL" || -z "$PROFILE" ]]; then
            echo "Usage: slice --model <path> --printer-profile <path>"
            exit 1
        fi
        
        # Run PrusaSlicer headless
        OUTPUT_GCODE="${MODEL%.*}.gcode"
        prusa-slicer --export-gcode --load "$PROFILE" "$MODEL" --output "$OUTPUT_GCODE"
        
        # Run p2pp post-processing
        p2pp "$OUTPUT_GCODE"
        
        echo "Post-processed G-code saved to: ${OUTPUT_GCODE%.gcode}.p2pp.gcode"
        ;;
    *)
        echo "Usage: $0 {slice} [options]"
        echo ""
        echo "Commands:"
        echo "  slice --model <model.3mf> --printer-profile <profile.ini>"
        echo ""
        echo "Examples:"
        echo "  $0 slice --model tests/models/multi-color.3mf --printer-profile profiles/palette3.ini"
        ;;
esac