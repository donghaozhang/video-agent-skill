#!/bin/bash
# Preprocess PR comment file for agentic evaluation
# Usage: ./preprocess.sh input.md [output.md]
# If output not specified, prints to stdout

set -e

INPUT_FILE=${1:-""}
OUTPUT_FILE=${2:-""}

if [ -z "$INPUT_FILE" ]; then
    echo "Usage: ./preprocess.sh input.md [output.md]"
    exit 1
fi

if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: File not found: $INPUT_FILE"
    exit 1
fi

# Extract content before <details> and remove HTML comments
preprocess() {
    local content
    # Get everything before <details>, remove HTML comments, trim trailing whitespace
    content=$(sed -n '1,/<details>/p' "$INPUT_FILE" | sed '/<details>/d' | sed 's/<!--.*-->//g' | sed '/^$/N;/^\n$/d')

    # Extract file path from the comment
    local file_path=$(grep -oP '(?<=\*\*File:\*\* `)[^`]+' "$INPUT_FILE" || echo "unknown")
    local line_num=$(grep -oP '(?<=\*\*Line:\*\* )[0-9]+' "$INPUT_FILE" || echo "unknown")

    cat << PROMPT
## Task

Evaluate this code review comment. Read the source file and determine if the issue is valid.

**Instructions:**
1. Read the file mentioned in the review: \`${file_path}\`
2. Check line ${line_num} and surrounding context
3. Determine if the review feedback is valid
4. If valid: Fix the issue in the code
5. If invalid: Explain why the feedback doesn't apply

**Important:** Be concise. Either fix the code or explain in 2-3 sentences why it's not applicable.

---

${content}
PROMPT
}

if [ -n "$OUTPUT_FILE" ]; then
    preprocess > "$OUTPUT_FILE"
    echo "Preprocessed: $INPUT_FILE -> $OUTPUT_FILE"
else
    preprocess
fi
