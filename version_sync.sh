#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./version_sync.sh            # uses latest tag (e.g. v0.1.2)
#   ./version_sync.sh v0.1.2     # or pass a specific tag
#
# Requirements:
# - Tag format: vMAJOR.MINOR.PATCH (e.g., v0.1.2)

# --- pick tag ---
if [[ $# -ge 1 ]]; then
  TAG="$1"
else
  TAG=$(git describe --tags --abbrev=0 2>/dev/null || true)
fi

if [[ -z "${TAG:-}" ]]; then
  echo "❌ No tag found. Create one first: git tag v0.1.2 && git push origin v0.1.2"
  exit 1
fi

if [[ ! "$TAG" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "❌ Tag '$TAG' does not match vMAJOR.MINOR.PATCH"
  exit 1
fi

VERSION="${TAG#v}"

# --- sanity checks ---
if [[ -n $(git status --porcelain) ]]; then
  echo "❌ Working tree not clean. Commit/stash changes first."
  exit 1
fi

if [[ ! -f pyproject.toml ]]; then
  echo "❌ pyproject.toml not found in current directory."
  exit 1
fi

# --- show current version ---
CURRENT=$(grep -E '^version *= *"' pyproject.toml | sed -E 's/.*"([^"]+)".*/\1/' || true)
echo "📄 pyproject.toml version: ${CURRENT:-<none>}"
echo "🏷  git tag version     : $VERSION"

if [[ "$CURRENT" == "$VERSION" ]]; then
  echo "✅ Already in sync. Nothing to do."
  exit 0
fi

# --- in-place edit (BSD/macOS sed vs GNU sed) ---
if sed --version >/dev/null 2>&1; then
  # GNU sed
  sed -i -E "s/^version *= *\"[^\"]+\"/version = \"$VERSION\"/" pyproject.toml
else
  # BSD/macOS sed
  sed -i '' -E "s/^version *= *\"[^\"]+\"/version = \"$VERSION\"/" pyproject.toml
fi

# verify write
NEW=$(grep -E '^version *= *"' pyproject.toml | sed -E 's/.*"([^"]+)".*/\1/')
if [[ "$NEW" != "$VERSION" ]]; then
  echo "❌ Failed to write version to pyproject.toml"
  exit 1
fi

git add pyproject.toml
git commit -m "Bump version to $VERSION (from tag $TAG)"
git push

echo "✅ Synced pyproject.toml to $VERSION and pushed commit."
