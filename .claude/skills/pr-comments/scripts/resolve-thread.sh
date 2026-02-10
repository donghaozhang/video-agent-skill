#!/bin/bash
# Resolve a PR review thread on GitHub and move task to completed
# Usage: ./resolve-thread.sh owner/repo pr_number comment_id [task_file]

set -e

REPO=${1:-""}
PR=${2:-""}
COMMENT_ID=${3:-""}
TASK_FILE=${4:-""}

if [ -z "$REPO" ] || [ -z "$PR" ] || [ -z "$COMMENT_ID" ]; then
    echo "Usage: ./resolve-thread.sh owner/repo pr_number comment_id [task_file]"
    echo "Example: ./resolve-thread.sh donghaozhang/qcut 102 2742327370 .github/pr-history/pr-102-tasks/comment.md"
    exit 1
fi

OWNER=$(echo "$REPO" | cut -d'/' -f1)
REPO_NAME=$(echo "$REPO" | cut -d'/' -f2)

echo "Finding thread for comment $COMMENT_ID in $REPO PR #$PR..."

# Get all review threads and find the one containing our comment
THREAD_ID=$(gh api graphql -f query="query {
  repository(owner: \"$OWNER\", name: \"$REPO_NAME\") {
    pullRequest(number: $PR) {
      reviewThreads(first: 100) {
        nodes {
          id
          isResolved
          comments(first: 10) {
            nodes {
              databaseId
            }
          }
        }
      }
    }
  }
}" --jq ".data.repository.pullRequest.reviewThreads.nodes[] | select(.comments.nodes[].databaseId == $COMMENT_ID) | .id" 2>/dev/null | head -1)

if [ -z "$THREAD_ID" ]; then
    echo "Error: Could not find thread for comment $COMMENT_ID"
    exit 1
fi

echo "Found thread: $THREAD_ID"

# Check if already resolved
IS_RESOLVED=$(gh api graphql -f query="query {
  repository(owner: \"$OWNER\", name: \"$REPO_NAME\") {
    pullRequest(number: $PR) {
      reviewThreads(first: 100) {
        nodes {
          id
          isResolved
        }
      }
    }
  }
}" --jq ".data.repository.pullRequest.reviewThreads.nodes[] | select(.id == \"$THREAD_ID\") | .isResolved" 2>/dev/null)

if [ "$IS_RESOLVED" = "true" ]; then
    echo "✓ Thread is already resolved"
else
    # Resolve the thread
    echo "Resolving thread..."
    RESULT=$(gh api graphql -f query="mutation {
      resolveReviewThread(input: {threadId: \"$THREAD_ID\"}) {
        thread {
          id
          isResolved
        }
      }
    }" 2>/dev/null)

    RESOLVED=$(echo "$RESULT" | jq -r '.data.resolveReviewThread.thread.isResolved')

    if [ "$RESOLVED" = "true" ]; then
        echo "✓ Thread resolved successfully"
    else
        echo "Error: Failed to resolve thread"
        echo "$RESULT" | jq .
        exit 1
    fi
fi

# Move task file to completed folder if provided
if [ -n "$TASK_FILE" ] && [ -f "$TASK_FILE" ]; then
    TASK_DIR=$(dirname "$TASK_FILE")
    COMPLETED_DIR="${TASK_DIR}_completed"
    FILENAME=$(basename "$TASK_FILE")

    mkdir -p -- "$COMPLETED_DIR"
    mv -- "$TASK_FILE" "$COMPLETED_DIR/$FILENAME"

    echo "✓ Task moved to: $COMPLETED_DIR/$FILENAME"
elif [ -n "$TASK_FILE" ]; then
    echo "Warning: Task file not found: $TASK_FILE"
fi

echo ""
echo "Done!"
