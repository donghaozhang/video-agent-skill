#!/bin/bash
# PR Comments Exporter - All Comments (Thread + Review)
# Usage: ./export-all.sh owner/repo pr_number [output_dir]

set -e

REPO=${1:-""}
PR=${2:-""}
OUTPUT_DIR=${3:-".github/pr-history/pr-${PR}-all"}

# Validate arguments
if [ -z "$REPO" ] || [ -z "$PR" ]; then
    echo "Usage: ./export-all.sh owner/repo pr_number [output_dir]"
    echo "Example: ./export-all.sh donghaozhang/qcut 102"
    exit 1
fi

# Check dependencies
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "Error: jq is not installed"
    exit 1
fi

# Create output directories
mkdir -p "$OUTPUT_DIR/thread"
mkdir -p "$OUTPUT_DIR/review"

echo "=========================================="
echo "Exporting all comments from $REPO PR #${PR}"
echo "=========================================="

# ===== THREAD COMMENTS (Issue Comments) =====
echo ""
echo "--- Main Thread Comments ---"

THREAD_TEMP=$(mktemp)
trap "rm -f $THREAD_TEMP" EXIT

gh api "repos/${REPO}/issues/${PR}/comments" > "$THREAD_TEMP" 2>/dev/null || {
    echo "Warning: Could not fetch thread comments"
}

thread_count=$(jq 'length' "$THREAD_TEMP" 2>/dev/null || echo "0")
echo "Found $thread_count thread comments"

for ((i=0; i<thread_count; i++)); do
    id=$(jq -r ".[$i].id" "$THREAD_TEMP")
    user=$(jq -r ".[$i].user.login" "$THREAD_TEMP")
    created=$(jq -r ".[$i].created_at | split(\"T\")[0]" "$THREAD_TEMP")
    body=$(jq -r ".[$i].body" "$THREAD_TEMP")
    html_url=$(jq -r ".[$i].html_url" "$THREAD_TEMP")

    # Create filename with index for ordering
    filename="${OUTPUT_DIR}/thread/$(printf "%02d" $((i+1)))_${user}_${id}.md"

    echo "[$((i+1))/$thread_count] $(basename "$filename")"

    cat > "$filename" << ENDFILE
# Thread Comment

- **Author:** ${user}
- **Date:** ${created}
- **Comment ID:** ${id}
- **URL:** ${html_url}

---

${body}
ENDFILE
done

# ===== REVIEW COMMENTS (Inline Code Comments) =====
echo ""
echo "--- Inline Review Comments ---"

REVIEW_TEMP=$(mktemp)
gh api "repos/${REPO}/pulls/${PR}/comments" > "$REVIEW_TEMP" 2>/dev/null || {
    echo "Warning: Could not fetch review comments"
}

review_count=$(jq 'length' "$REVIEW_TEMP" 2>/dev/null || echo "0")
echo "Found $review_count review comments"

for ((i=0; i<review_count; i++)); do
    id=$(jq -r ".[$i].id" "$REVIEW_TEMP")
    user=$(jq -r ".[$i].user.login" "$REVIEW_TEMP")
    path=$(jq -r ".[$i].path" "$REVIEW_TEMP")
    line=$(jq -r ".[$i].line // .[$i].original_line" "$REVIEW_TEMP")
    created=$(jq -r ".[$i].created_at | split(\"T\")[0]" "$REVIEW_TEMP")
    body=$(jq -r ".[$i].body" "$REVIEW_TEMP")
    html_url=$(jq -r ".[$i].html_url" "$REVIEW_TEMP")

    safe_path=$(echo "$path" | sed 's/[\/\\]/-/g')
    filename="${OUTPUT_DIR}/review/${user}_${safe_path}_L${line}_${id}.md"

    echo "[$((i+1))/$review_count] $(basename "$filename")"

    cat > "$filename" << ENDFILE
# Review Comment

- **Author:** ${user}
- **File:** \`${path}\`
- **Line:** ${line}
- **Date:** ${created}
- **Comment ID:** ${id}
- **URL:** ${html_url}

---

${body}
ENDFILE
done

rm -f "$REVIEW_TEMP"

# ===== SUMMARY =====
echo ""
echo "=========================================="
echo "Export Complete!"
echo "=========================================="
echo "Thread comments: $thread_count -> $OUTPUT_DIR/thread/"
echo "Review comments: $review_count -> $OUTPUT_DIR/review/"
echo "Total: $((thread_count + review_count)) files"
echo ""
echo "Directory structure:"
ls -la "$OUTPUT_DIR/"
