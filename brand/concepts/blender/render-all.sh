#!/bin/sh
# Renders all four Kinton directions at full size into ../  (blender on PATH)
cd "$(dirname "$0")"
for d in keyhole direct sealed arc; do blender -b -P kinton.py -- "$d" "$PWD/../$d-full.png" "${SIZE:-1024}" "${SAMPLES:-160}" 2>&1 | grep -E "rendered|Error|Traceback"; done
