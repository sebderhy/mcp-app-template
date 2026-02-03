#!/usr/bin/env bash
#
# create_new_app.sh - Initialize a new MCP App by removing example widgets
#
# Usage:
#   ./create_new_app.sh                        # Remove all example widgets
#   ./create_new_app.sh --keep carousel        # Keep carousel as starting point
#   ./create_new_app.sh --keep carousel,todo   # Keep multiple widgets
#   ./create_new_app.sh --name my-app          # Set app name
#   ./create_new_app.sh --keep carousel --name my-app
#
# This script:
#   1. Removes example widget directories from src/ and server/widgets/
#   2. Cleans unused dependencies from package.json
#   3. Sets APP_NAME in .env (if --name provided)
#   4. Runs build and tests to verify everything works
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# All example widgets in this template
ALL_WIDGETS=(
    "boilerplate"
    "carousel"
    "dashboard"
    "gallery"
    "list"
    "map"
    "qr"
    "scenario-modeler"
    "shop"
    "solar-system"
    "system-monitor"
    "todo"
)

# Dependency map: which widgets need which packages
# Format: "package:widget1,widget2,..."
DEPENDENCY_MAP=(
    "three:solar-system"
    "@react-three/fiber:solar-system"
    "@react-three/drei:solar-system"
    "@react-three/postprocessing:solar-system"
    "@react-spring/three:solar-system"
    "@types/three:solar-system"
    "framer-motion:solar-system,shop,gallery,todo"
    "chart.js:scenario-modeler,system-monitor"
    "react-datepicker:todo"
    "@types/react-datepicker:todo"
    "react-router-dom:shop"
)

# Parse arguments
KEEP_WIDGETS=()
APP_NAME=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --keep)
            IFS=',' read -ra KEEP_WIDGETS <<< "$2"
            shift 2
            ;;
        --name)
            APP_NAME="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [--keep widget1,widget2] [--name app-name]"
            echo ""
            echo "Options:"
            echo "  --keep    Comma-separated list of widgets to keep (default: none)"
            echo "  --name    App name (written to .env as APP_NAME)"
            echo ""
            echo "Available widgets:"
            printf "  %s\n" "${ALL_WIDGETS[@]}"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Validate --keep widgets exist
for widget in "${KEEP_WIDGETS[@]}"; do
    if [[ ! -d "src/$widget" ]]; then
        echo "Error: Widget '$widget' not found in src/"
        echo ""
        echo "Available widgets:"
        printf "  %s\n" "${ALL_WIDGETS[@]}"
        exit 1
    fi
done

# Convert widget name to Python module name (hyphen to underscore)
widget_to_module() {
    echo "$1" | tr '-' '_'
}

# Check if a widget is in the keep list
is_kept() {
    local widget="$1"
    for kept in "${KEEP_WIDGETS[@]}"; do
        if [[ "$kept" == "$widget" ]]; then
            return 0
        fi
    done
    return 1
}

# Check if any widget in a list is kept
any_kept() {
    local widgets="$1"
    IFS=',' read -ra widget_list <<< "$widgets"
    for w in "${widget_list[@]}"; do
        if is_kept "$w"; then
            return 0
        fi
    done
    return 1
}

# Compute widgets to delete
WIDGETS_TO_DELETE=()
for widget in "${ALL_WIDGETS[@]}"; do
    if ! is_kept "$widget"; then
        WIDGETS_TO_DELETE+=("$widget")
    fi
done

if [[ ${#WIDGETS_TO_DELETE[@]} -eq 0 ]]; then
    echo "All widgets are being kept. Nothing to do."
    exit 0
fi

echo "============================================"
echo "Creating new MCP App"
echo "============================================"
echo ""
if [[ ${#KEEP_WIDGETS[@]} -gt 0 ]]; then
    echo "Keeping widgets: ${KEEP_WIDGETS[*]}"
else
    echo "Keeping widgets: (none)"
fi
echo "Removing widgets: ${WIDGETS_TO_DELETE[*]}"
echo ""

# Step 1: Delete frontend widget directories
echo "→ Removing frontend widget directories..."
for widget in "${WIDGETS_TO_DELETE[@]}"; do
    if [[ -d "src/$widget" ]]; then
        rm -rf "src/$widget"
        echo "  Deleted src/$widget/"
    fi
done

# Step 2: Delete server widget modules
echo "→ Removing server widget modules..."
for widget in "${WIDGETS_TO_DELETE[@]}"; do
    module_name=$(widget_to_module "$widget")
    module_path="server/widgets/${module_name}.py"
    if [[ -f "$module_path" ]]; then
        rm "$module_path"
        echo "  Deleted $module_path"
    fi
done

# Step 3: Clean package.json dependencies
echo "→ Cleaning unused dependencies from package.json..."
DEPS_TO_REMOVE=()
for entry in "${DEPENDENCY_MAP[@]}"; do
    package="${entry%%:*}"
    widgets="${entry#*:}"
    if ! any_kept "$widgets"; then
        DEPS_TO_REMOVE+=("$package")
    fi
done

if [[ ${#DEPS_TO_REMOVE[@]} -gt 0 ]]; then
    echo "  Removing packages: ${DEPS_TO_REMOVE[*]}"

    # Build JSON array of deps to remove
    DEPS_JSON="["
    for i in "${!DEPS_TO_REMOVE[@]}"; do
        if [[ $i -gt 0 ]]; then
            DEPS_JSON+=","
        fi
        DEPS_JSON+="\"${DEPS_TO_REMOVE[$i]}\""
    done
    DEPS_JSON+="]"

    # Use node to remove dependencies from package.json
    node -e "
const fs = require('fs');
const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
const depsToRemove = JSON.parse(process.argv[1]);

for (const dep of depsToRemove) {
    if (pkg.dependencies && pkg.dependencies[dep]) {
        delete pkg.dependencies[dep];
        console.log('    Removed from dependencies:', dep);
    }
    if (pkg.devDependencies && pkg.devDependencies[dep]) {
        delete pkg.devDependencies[dep];
        console.log('    Removed from devDependencies:', dep);
    }
}

fs.writeFileSync('package.json', JSON.stringify(pkg, null, 2) + '\n');
" "$DEPS_JSON"
else
    echo "  No dependencies to remove"
fi

# Step 4: Set APP_NAME in .env if provided
if [[ -n "$APP_NAME" ]]; then
    echo "→ Setting APP_NAME=$APP_NAME in .env..."
    if [[ -f ".env" ]]; then
        # Remove existing APP_NAME line if present
        grep -v "^APP_NAME=" .env > .env.tmp || true
        mv .env.tmp .env
    fi
    echo "APP_NAME=$APP_NAME" >> .env
fi

# Step 5: Update lockfile
echo "→ Updating lockfile..."
pnpm install --silent

# Step 6: Build and test
echo "→ Building widgets..."
pnpm run build

echo "→ Running tests..."
pnpm run test

echo ""
echo "============================================"
echo "Done!"
echo "============================================"
echo ""
if [[ ${#KEEP_WIDGETS[@]} -gt 0 ]]; then
    echo "Kept widgets: ${KEEP_WIDGETS[*]}"
else
    echo "All example widgets removed."
fi
echo "Removed: ${WIDGETS_TO_DELETE[*]}"
if [[ -n "$APP_NAME" ]]; then
    echo "App name: $APP_NAME"
fi
echo ""
echo "Next steps:"
echo "  1. Create your widget in src/my-widget/index.tsx"
echo "  2. Add the handler in server/widgets/my_widget.py"
echo "  3. Run: pnpm run build && pnpm run test"
echo "  4. Test: pnpm run server → http://localhost:8000/assets/apptester.html"
echo ""
