#!/usr/bin/env bash
set -euo pipefail

: "${GITVERSE_CREDS:?GITVERSE_CREDS must be set}"

git clone "https://${GITVERSE_CREDS}@gitverse.ru/dfint/data-mirror.git"
repo_dir="$PWD/data-mirror"
rm -rf "$repo_dir/autobuild" "$repo_dir/update-data"

wget https://github.com/dfint/autobuild/archive/refs/heads/gh-pages.zip
unzip -o gh-pages.zip
mkdir --parents "$repo_dir/autobuild"
cp --recursive autobuild-gh-pages/translation_build/ "$repo_dir/autobuild/translation_build"

mkdir --parents "$repo_dir/update-data"
cp --recursive deploy/metadata/ "$repo_dir/update-data/metadata"
cp --recursive deploy/store/ "$repo_dir/update-data/store"

cd "$repo_dir"
git pull
git add .
git config user.name "update-bot"
git config user.email "update-bot"

if git diff --cached --quiet; then
  echo "No changes to deploy"
else
  git commit -m "Update data"
  git push
fi
