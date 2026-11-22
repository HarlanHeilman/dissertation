# Dissertation, LaTeX version

The root file is `../main.tex`, at the top of the repository, because Overleaf compiles from the project root. Build with `latexmk main.tex` from the repository root (LuaLaTeX and biber, set in `../latexmkrc`). On Overleaf, set the main document to `main.tex` and the compiler to LuaLaTeX.

## Layout

- `../main.tex` sets the page order. `preamble.tex` holds packages, WSU page setup, and the title, author, and date macros.
- `frontmatter/` has the title, committee, abstract, acknowledgments, and dedication pages, in the order set by the WSU Thesis and Dissertation Formatting Guidelines v1.3 (January 2026).
- `chapters/` has one file per chapter. `appendices/` holds the supporting information, now Appendix A.
- `references.bib` was exported from the Zotero citations in the Word draft. Keys follow the pattern `authorYEARword`.
- All paths are written from the repository root. Figures are read from `figures/dissertation/word-export/` (images taken from the Word draft, named by figure number) and then `figures/dissertation/`.

## Origin

Converted on 2026-11-22 from `word/heilman-dissertation-final.docx` using pandoc 3.9 and the scripts in `../src/latex-conversion/`. Those scripts were run once. Rerunning them overwrites any edits made here.

## Known cleanup

- 19 captions, in Chapters 3, 4, and 5 and in Appendix A, contained equations that the Word text boxes stored as plain text. Each one is marked `% TODO caption contains equations`.
- The 65 display equations are unnumbered `\[ \]` blocks. Equation numbers from Word were not carried over.
- Figure and table references are now `\ref`. Chapter references ("Chapter 4", 70 of them) are still plain text.
- "Fig. 4" in Appendix A refers to the numbering of the published manuscript and was left as written.
- Table headers that used Word equations came through as display math inside minipages and should be simplified.
- Figure 2.4 (`fig2-04_polymer-nexafs.png`) is a 440 px bitmap recovered from the EMF in the Word file, the only copy found on disk or in earlier drafts.
- WSU asks that the first page of each manuscript chapter carry the full citation or the statement "Prepared for submission to an academic journal."
