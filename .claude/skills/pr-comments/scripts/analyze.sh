#!/bin/bash
# Analyze PR comment task files - group by source file
# Usage: ./analyze.sh tasks_dir

set -e

TASKS_DIR=${1:-""}

if [ -z "$TASKS_DIR" ]; then
    echo "Usage: ./analyze.sh tasks_dir"
    echo "Example: ./analyze.sh .github/pr-history/pr-102-tasks"
    exit 1
fi

if [ ! -d "$TASKS_DIR" ]; then
    echo "Error: Directory not found: $TASKS_DIR"
    exit 1
fi

echo "# PR Comments Analysis"
echo ""
echo "Tasks directory: $TASKS_DIR"
echo ""

# Extract source files and line numbers from task files
declare -A file_comments

total=0
for task in "$TASKS_DIR"/*.md; do
    if [ -f "$task" ]; then
        # Extract file path from task content
        source_file=$(grep -oP '(?<=\*\*File:\*\* `)[^`]+' "$task" 2>/dev/null || echo "unknown")
        line=$(grep -oP '(?<=\*\*Line:\*\* )[0-9]+' "$task" 2>/dev/null || echo "?")

        if [ -n "${file_comments[$source_file]}" ]; then
            file_comments[$source_file]="${file_comments[$source_file]},$line"
        else
            file_comments[$source_file]="$line"
        fi
        total=$((total + 1))
    fi
done

echo "## Summary"
echo "- Total comments: $total"
echo "- Unique files: ${#file_comments[@]}"
echo ""

echo "## By Source File (process in this order)"
echo ""
echo "| Source File | Lines (fix bottom-up) | Count |"
echo "|-------------|----------------------|-------|"

for source_file in "${!file_comments[@]}"; do
    lines="${file_comments[$source_file]}"
    # Sort lines descending
    sorted_lines=$(echo "$lines" | tr ',' '\n' | sort -rn | tr '\n' ',' | sed 's/,$//')
    count=$(echo "$lines" | tr ',' '\n' | wc -l)
    echo "| \`$source_file\` | $sorted_lines | $count |"
done | sort -t'|' -k4 -rn

echo ""
echo "## Recommended Processing Order"
echo ""
echo "Fix each file's comments **bottom-up** (highest line number first)."
echo "This prevents line number shifts from affecting subsequent fixes."
