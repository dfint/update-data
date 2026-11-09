#!/usr/bin/env bash
set -euo pipefail

: "${GITVERSE_CREDS:?GITVERSE_CREDS must be set}"

git clone "https://${GITVERSE_CREDS}@gitverse.ru/dfint/data-mirror.git"
cd data-mirror
rm -rf autobuild update-data

wget https://github.com/dfint/autobuild/archive/refs/heads/gh-pages.zip
unzip gh-pages.zip
mkdir --parents autobuild
cp --recursive autobuild-gh-pages/translation_build/ autobuild/translation_build

mkdir --parents update-data
cp --recursive ../deploy/metadata/ update-data/metadata
cp --recursive ../deploy/store/ update-data/store

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
