#!/bin/bash

VERSION=$1

if [ -z "$VERSION" ]; then
  echo "Usage: bash trendforge_install.sh [version]"
  exit 1
fi

INSTALLER="/root/trendforge-mvp/installers/v$VERSION.sh"

if [ ! -f "$INSTALLER" ]; then
  echo "Installer not found for version $VERSION"
  exit 1
fi

echo "================================"
echo "TrendForge Installer"
echo "Installing Version: $VERSION"
echo "================================"

bash $INSTALLER

echo "================================"
echo "Install Finished"
echo "================================"
