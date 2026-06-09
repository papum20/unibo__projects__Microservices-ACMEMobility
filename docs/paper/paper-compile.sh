#!/bin/bash

# Find docs/paper/ absolute path before cd
PAPER_DIR=$(find . -type d -path "*/docs/paper" 2>/dev/null | head -n 1)
if [ -n "$PAPER_DIR" ]; then
    PAPER_DIR_ABS=$(cd "$PAPER_DIR" && pwd)
else
    echo "Error: Could not find docs/paper/ directory"
    exit 1
fi


cd "$PAPER_DIR_ABS"

rm -f main.pdf main.aux main.bbl main.blg main.out main.log *.aux *.bbl *.blg

pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
