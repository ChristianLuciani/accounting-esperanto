#!/usr/bin/env bash
# Build the arXiv source tarball for the Kontablo preprint.
#
# Produces a source-only tarball (main .tex + clapps.cls + sections/ + figures/)
# that compiles standalone, verifies it compiles, and writes it to
# docs/papers/arxiv/kontablo-arxiv-src.tar.gz.
#
# Requires a TeX distribution with latexmk + pdflatex on PATH. On this machine:
#   export PATH="/usr/local/texlive/2024basic/bin/universal-darwin:$PATH"
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/docs/papers/drafts"
OUT="$ROOT/docs/papers/arxiv/kontablo-arxiv-src.tar.gz"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

mkdir -p "$STAGE/sections" "$STAGE/figures"
cp "$SRC/kontablo_preprint_modular.tex" "$SRC/clapps.cls" "$STAGE/"
cp "$SRC"/sections/*.tex "$STAGE/sections/"
cp "$SRC"/figures/*.tex "$STAGE/figures/"
cp "$SRC"/figures/fig_tree_graph_tree.pdf "$STAGE/figures/"

# Verify the staged source compiles in isolation before packaging.
( cd "$STAGE" && latexmk -pdf -interaction=nonstopmode -halt-on-error \
    kontablo_preprint_modular.tex >/dev/null )
pages="$(cd "$STAGE" && pdfinfo kontablo_preprint_modular.pdf | awk '/Pages/{print $2}')"
echo "Staged source compiles: ${pages} pages"

# Strip build artifacts so the tarball is source-only.
( cd "$STAGE" && latexmk -c >/dev/null 2>&1 || true )
rm -f "$STAGE"/kontablo_preprint_modular.pdf "$STAGE"/kontablo_preprint_modular.toc

mkdir -p "$(dirname "$OUT")"
tar -czf "$OUT" -C "$STAGE" .
echo "Wrote $OUT"
