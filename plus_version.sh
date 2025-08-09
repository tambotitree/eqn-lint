#!/usr/bin/env bash
# plus_version.sh - bump minor version from git tag and update pyproject.toml

set -euo pipefail

PYPROJECT="pyproject.toml"
PUSH=${PUSH:-0}

# Ensure working tree is clean
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "ERROR: Working tree is not clean."
    exit 1
fi

# Get latest tag
LATEST_TAG=$(git tag --sort=-v:refname | head -n1 || true)
if ! echo "$LATEST_TAG" | grep -Eq '^v[0-9]+\.[0-9]+\.[0-9]+$'; then
    echo "ERROR: No tag found in format vX.Y.Z."
    exit 1
fi

VER=${LATEST_TAG#v}
MAJOR=$(echo "$VER" | cut -d. -f1)
MINOR=$(echo "$VER" | cut -d. -f2)
PATCH=$(echo "$VER" | cut -d. -f3)

NEW_MINOR=$((MINOR + 1))
NEW_VER="${MAJOR}.${NEW_MINOR}.0"
NEW_TAG="v${NEW_VER}"

echo "Current tag : $LATEST_TAG"
echo "New version : $NEW_TAG"

if [ ! -f "$PYPROJECT" ]; then
    echo "ERROR: $PYPROJECT not found."
    exit 1
fi

# Choose sed syntax for platform
if sed --version >/dev/null 2>&1; then
    SED_INPLACE=(sed -i -E)
else
    SED_INPLACE=(sed -i '' -E)
fi

# Update version line
"${SED_INPLACE[@]}" \
    "s/^([[:space:]]*version[[:space:]]*=[[:space:]]*\")[0-9]+\.[0-9]+\.[0-9]+(\")/\1${NEW_VER}\2/" \
    "$PYPROJECT"

# Verify update
grep -q "^version = \"${NEW_VER}\"" "$PYPROJECT" || {
    echo "ERROR: Failed to update version in $PYPROJECT"
    exit 1
}

git add "$PYPROJECT"
git commit -m "Bump version to ${NEW_TAG}"
git tag -a "${NEW_TAG}" -m "Release ${NEW_TAG}"

echo "Bumped version and created tag ${NEW_TAG}."

if [ "$PUSH" = "1" ]; then
    git push origin main
    git push origin "${NEW_TAG}"
    echo "Pushed main and ${NEW_TAG}."
fi
