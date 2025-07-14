#!/bin/bash
# Remove all Django migration files except __init__.py in project apps only
# Usage: ./scripts/clean_migrations.sh

set -e

echo "Cleaning Django migration files in project apps only..."

# Only clean migrations in the router_supervisor project directory
find /code/router_supervisor -type d -name migrations | while read dir; do
    echo "Cleaning $dir ..."
    find "$dir" -type f \( -name '*.py' -or -name '*.pyc' \) ! -name '__init__.py' -delete
    echo "  -> Done."
done

echo "✅ All project migration files (except __init__.py) have been removed."
echo "You can now restart your containers to let Docker auto-generate migrations."
