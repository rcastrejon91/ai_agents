#!/bin/bash

# Self-healing autofix script for the AI agents repository
# This script validates and fixes package.json files before running formatters
# to prevent workflow crashes from malformed JSON files.

set -e

echo "🔧 Starting self-healing autofix workflow..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to log with timestamp
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

# Function to validate and fix package.json files
validate_and_fix_package_json() {
    log "🔍 Validating and fixing package.json files..."
    
    # Find all package.json files excluding node_modules and other irrelevant directories
    find . -name "package.json" -type f \
        -not -path "*/node_modules/*" \
        -not -path "*/.next/*" \
        -not -path "*/dist/*" \
        -not -path "*/.git/*" | while read -r file; do
        echo "Checking: $file"
        
        # Try to parse the JSON
        if ! node -e "JSON.parse(require('fs').readFileSync('$file', 'utf8'))" 2>/dev/null; then
            echo -e "${YELLOW}⚠️  Invalid JSON in $file, attempting to fix...${NC}"
            
            # Create a backup
            cp "$file" "$file.backup"
            
            # Try to fix common JSON issues using a Node.js script
            node -e "
                const fs = require('fs');
                try {
                    let content = fs.readFileSync('$file', 'utf8');
                    
                    // Remove trailing commas (common issue)
                    content = content.replace(/,(\s*[}\]])/g, '\$1');
                    
                    // Try to parse and reformat
                    const parsed = JSON.parse(content);
                    const formatted = JSON.stringify(parsed, null, 2);
                    fs.writeFileSync('$file', formatted);
                    console.log('✅ Fixed and formatted $file');
                } catch (error) {
                    console.error('❌ Could not fix $file:', error.message);
                    // Restore backup if we can't fix it
                    if (fs.existsSync('$file.backup')) {
                        fs.copyFileSync('$file.backup', '$file');
                    }
                    process.exit(1);
                }
            " || {
                echo -e "${RED}❌ Failed to fix $file, restoring backup${NC}"
                if [ -f "$file.backup" ]; then
                    mv "$file.backup" "$file"
                fi
                continue
            }
            
            # Clean up backup if successful
            rm -f "$file.backup"
        else
            echo -e "${GREEN}✅ Valid JSON: $file${NC}"
            
            # Format the valid JSON for consistency
            node -e "
                const fs = require('fs');
                const content = fs.readFileSync('$file', 'utf8');
                const parsed = JSON.parse(content);
                const formatted = JSON.stringify(parsed, null, 2);
                fs.writeFileSync('$file', formatted);
            "
        fi
    done
    
    log "✅ Package.json validation complete"
}

# Function to setup Node.js and run formatters
run_js_formatters() {
    # Check if we have any package.json files
    if [ -z "$(find . -name "package.json" -type f)" ]; then
        log "⏭️  No package.json files found, skipping JS/TS formatting"
        return 0
    fi
    
    log "📦 Setting up Node.js environment..."
    
    # Install dependencies safely
    if [ -f "package.json" ]; then
        log "Installing dependencies..."
        if ! npm ci 2>/dev/null; then
            log "⚠️  npm ci failed, trying npm install..."
            npm install || {
                log "❌ npm install failed, but continuing with available tools"
            }
        fi
    fi
    
    log "🔧 Running ESLint with fixes..."
    if npx --yes eslint . --ext .js,.ts,.jsx,.tsx --fix 2>/dev/null; then
        log "✅ ESLint completed successfully"
    else
        log "⚠️  ESLint encountered some issues, but continuing..."
    fi
    
    log "💅 Running Prettier..."
    if npx --yes prettier . --write 2>/dev/null; then
        log "✅ Prettier completed successfully"
    else
        log "⚠️  Prettier encountered some issues, but continuing..."
    fi
    
    log "✅ JavaScript/TypeScript formatting complete"
}

# Function to run Python formatters
run_python_formatters() {
    # Check if we have any Python files
    if [ -z "$(find . -name "*.py" -type f)" ]; then
        log "⏭️  No Python files found, skipping Python formatting"
        return 0
    fi
    
    log "🐍 Setting up Python environment..."
    
    # Install Python tools
    python -m pip install --upgrade pip --quiet
    python -m pip install ruff black isort --quiet || {
        log "⚠️  Some Python tools failed to install, continuing with available ones..."
    }
    
    log "🔧 Running Ruff..."
    ruff check . --fix || {
        log "⚠️  Ruff encountered some issues, but continuing..."
    }
    
    log "📏 Running isort..."
    isort . || {
        log "⚠️  isort encountered some issues, but continuing..."
    }
    
    log "⚫ Running Black..."
    black . || {
        log "⚠️  Black encountered some issues, but continuing..."
    }
    
    log "✅ Python formatting complete"
}

# Function to commit changes
commit_changes() {
    log "📝 Checking for changes to commit..."
    
    # Configure git
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
    
    # Add all changes
    git add -A
    
    # Don't commit workflow files (GitHub blocks this)
    git restore --staged .github/workflows || true
    
    # Check if there are changes to commit
    if git diff --cached --quiet; then
        log "🎉 No changes to commit"
        return 0
    fi
    
    # Show what we're about to commit
    log "Changes to commit:"
    git diff --cached --name-only
    
    # Fetch latest changes and rebase if needed
    git fetch origin main || true
    git rebase origin/main || {
        log "⚠️  Rebase had conflicts, but continuing with commit..."
    }
    
    # Commit and push
    git commit -m "chore: autofix (package.json validation, ESLint/Prettier, Ruff/Black/isort)" || {
        log "⚠️  Commit failed, but workflow completed"
        return 0
    }
    
    git push origin HEAD:main || {
        log "⚠️  Push failed, but changes are committed locally"
        return 0
    }
    
    log "✅ Changes committed and pushed successfully"
}

# Main execution flow
main() {
    log "🚀 Starting self-healing autofix process"
    
    # Step 1: Validate and fix package.json files
    validate_and_fix_package_json
    
    # Step 2: Run JavaScript/TypeScript formatters
    run_js_formatters
    
    # Step 3: Run Python formatters  
    run_python_formatters
    
    # Step 4: Commit changes
    commit_changes
    
    log "🎉 Self-healing autofix workflow completed successfully!"
}

# Run main function
main "$@"