#!/usr/bin/env bash
set -euo pipefail

APP_NAME="Whimsy"
APP_DIR="dist/${APP_NAME}.app"
CONTENTS_DIR="${APP_DIR}/Contents"
MACOS_DIR="${CONTENTS_DIR}/MacOS"
RESOURCES_DIR="${CONTENTS_DIR}/Resources"

echo "Building ${APP_DIR}..."

rm -rf "${APP_DIR}"
mkdir -p "${MACOS_DIR}" "${RESOURCES_DIR}"

# Determine actual project root to embed in the launcher (so the app works even if moved)
PROJECT_ROOT="$(pwd)"

# Create Info.plist
cat > "${CONTENTS_DIR}/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launcher</string>
    <key>CFBundleIdentifier</key>
    <string>com.whimsy.controlpanel</string>
    <key>CFBundleName</key>
    <string>${APP_NAME}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.10.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

# Create Launcher Script
# We hardcode PROJECT_ROOT so the app finds the environment even if moved to Applications
cat > "${MACOS_DIR}/launcher" <<EOF
#!/usr/bin/env bash
exec "${PROJECT_ROOT}/.venv/bin/python" "${PROJECT_ROOT}/whimsy_gui.py"
EOF

chmod +x "${MACOS_DIR}/launcher"

echo "Done. You can find the app at:"
echo "  ${APP_DIR}"
echo ""
echo "You can move '${APP_NAME}.app' to /Applications or your Dock."
echo "Note: It depends on the source files in ${PROJECT_ROOT} - do not delete them."
