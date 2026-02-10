#!/bin/bash
# PR Comments Exporter
# Usage: ./export.sh owner/repo pr_number [output_dir]

set -e

REPO=${1:-""}
PR=${2:-""}
OUTPUT_DIR=${3:-".github/pr-history/pr-${PR}"}

# Validate arguments
if [ -z "$REPO" ] || [ -z "$PR" ]; then
    echo "Usage: ./export.sh owner/repo pr_number [output_dir]"
    echo "Example: ./export.sh donghaozhang/qcut 102"
    exit 1
fi

# Validate PR is numeric to prevent path traversal
if ! [[ "$PR" =~ ^[0-9]+$ ]]; then
    echo "Error: PR number must be numeric, got: $PR"
    exit 1
fi

# Check dependencies
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "Error: jq is not installed"
    echo "Install it from: https://stedolan.github.io/jq/"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "Fetching review comments from $REPO PR #${PR}..."

# Fetch all comments once and save to temp file
TEMP_FILE=$(mktemp)
trap "rm -f $TEMP_FILE" EXIT

gh api "repos/${REPO}/pulls/${PR}/comments" > "$TEMP_FILE" 2>/dev/null || {
    echo "Error: Failed to fetch PR comments. Check that:"
    echo "  - Repository '$REPO' exists"
    echo "  - PR #$PR exists"
    echo "  - You have access to the repository"
    echo "  - GitHub CLI is authenticated (run: gh auth status)"
    exit 1
}

count=$(jq 'length' "$TEMP_FILE")
echo "Found $count review comments"

if [ "$count" -eq "0" ]; then
    echo "No review comments found on this PR."
    echo "Note: This exports inline code review comments, not main thread comments."
    echo "For main thread comments, use: gh api repos/${REPO}/issues/${PR}/comments"
    exit 0
fi

# Loop through each comment
for ((i=0; i<count; i++)); do
    id=$(jq -r ".[$i].id" "$TEMP_FILE")
    user=$(jq -r ".[$i].user.login" "$TEMP_FILE")
    path=$(jq -r ".[$i].path" "$TEMP_FILE")
    line=$(jq -r ".[$i].line // .[$i].original_line" "$TEMP_FILE")
    created=$(jq -r ".[$i].created_at | split(\"T\")[0]" "$TEMP_FILE")
    body=$(jq -r ".[$i].body" "$TEMP_FILE")
    html_url=$(jq -r ".[$i].html_url" "$TEMP_FILE")

    # Create safe filename (replace path separators with dashes)
    safe_path=$(echo "$path" | sed 's/[\/\\]/-/g')
    filename="${OUTPUT_DIR}/${user}_${safe_path}_L${line}_${id}.md"

    echo "[$((i+1))/$count] Creating: $(basename "$filename")"

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

echo ""
echo "Done! $count files saved to: $OUTPUT_DIR/"
echo ""
echo "Files created:"
ls -1 "$OUTPUT_DIR/"
