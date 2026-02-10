#!/bin/bash
# Batch preprocess all PR comment files in a directory
# Usage: ./batch-preprocess.sh input_dir output_dir

set -e

INPUT_DIR=${1:-""}
OUTPUT_DIR=${2:-""}

if [ -z "$INPUT_DIR" ]; then
    echo "Usage: ./batch-preprocess.sh input_dir output_dir"
    echo "Example: ./batch-preprocess.sh .github/pr-history/pr-102 .github/pr-history/pr-102-tasks"
    exit 1
fi

if [ ! -d "$INPUT_DIR" ]; then
    echo "Error: Directory not found: $INPUT_DIR"
    exit 1
fi

# Default output dir
if [ -z "$OUTPUT_DIR" ]; then
    OUTPUT_DIR="${INPUT_DIR}-tasks"
fi

mkdir -p "$OUTPUT_DIR"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

count=0
for file in "$INPUT_DIR"/*.md; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        # Skip README
        if [ "$filename" = "README.md" ]; then
            continue
        fi

        output_file="${OUTPUT_DIR}/${filename}"
        bash "$SCRIPT_DIR/preprocess.sh" "$file" "$output_file"
        count=$((count + 1))
    fi
done

echo ""
echo "Done! Preprocessed $count files"
echo "Output directory: $OUTPUT_DIR"
echo ""
echo "Files ready for evaluation:"
ls -1 "$OUTPUT_DIR/"
