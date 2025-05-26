#!/bin/bash

# Usage: ./instantiate-template.sh new_project_name
# This replaces all instances of 'python_template' with 'new_project_name'

set -euo pipefail

NEW_NAME="${1:-}"
OLD_NAME="python_template"

if [ -z "$NEW_NAME" ]; then
  echo "Usage: $0 new_project_name"
  exit 1
fi

echo "Replacing all instances of '${OLD_NAME}' with '${NEW_NAME}'..."

mv "./src/${OLD_NAME}" "./src/${NEW_NAME}"

# Replace in src
find "./src/${NEW_NAME}" -type f -exec sed -i '' "s/${OLD_NAME}/${NEW_NAME}/g" {} \;

# Replace in tests
find "./tests" -type f -exec sed -i '' "s/${OLD_NAME}/${NEW_NAME}/g" {} \;

# Replace in readme
sed -i '' "s/${OLD_NAME}/${NEW_NAME}/g" "./README.md"

# Reaplace in pyproject.toml
sed -i '' "s/${OLD_NAME}/${NEW_NAME}/g" "./pyproject.toml"

echo "Replaced all instances of '${OLD_NAME}' with '${NEW_NAME}' in './src/${NEW_NAME}'"

echo "Template instantiation complete. New package name: '${NEW_NAME}'"
