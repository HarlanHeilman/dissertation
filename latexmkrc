# Read by latexmk locally and by Overleaf. Set the Overleaf compiler to LuaLaTeX as well.
$pdf_mode = 4;   # LuaLaTeX
$bibtex_use = 2; # run biber when the .bib changes
# Locally, `latexmk` with no argument builds both the dissertation and the supplemental file.
@default_files = ('main.tex', 'supplement.tex');
