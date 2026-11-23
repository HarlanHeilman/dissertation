# Read by latexmk locally and by Overleaf. Set the Overleaf compiler to LuaLaTeX as well.
$pdf_mode = 4;   # LuaLaTeX
$bibtex_use = 2; # run biber when the .bib changes
# Locally, `latexmk` with no argument builds both the dissertation and the supplemental file.
@default_files = ('main.tex', 'supplement.tex');

# On the Mac, every file of the build (.aux, .log, .bbl, .toc, .fls, the chapter .aux files and so on) goes to build/,
# and the finished PDF is copied next to main.tex, so the root holds only main.pdf and supplement.pdf.
# `latexmk -C` empties build/; delete the copied PDFs by hand if wanted.
# Overleaf runs on Linux and manages its own output directory, so it is left alone.
if ($^O eq 'darwin') {
  $out_dir = 'build';
  $aux_dir = 'build';
  $success_cmd = 'cp %D .';
  use File::Path qw(make_path);
  make_path('build/latex/chapters', 'build/latex/supplement', 'build/latex/frontmatter');
}
