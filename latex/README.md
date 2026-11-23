# Dissertation, LaTeX version

Two documents are built from the repository root, each with LuaLaTeX and biber (`latexmkrc` sets both):

- `main.tex`, the dissertation.
- `supplement.tex`, the supporting information for Chapter 4, uploaded to ProQuest as a separate supplemental file. Figures, tables, sections and equations there are numbered S1, S2, and so on.

`latexmk` with no argument builds both. On Overleaf, set the compiler to LuaLaTeX and the main document to `main.tex`, and switch the main document to `supplement.tex` to build the supplement.

## Layout

- `latex/preamble.tex` holds packages, page setup, fonts, heading and list styles, and the title, author and date macros. All paths are written from the repository root.
- `latex/frontmatter/` has the title, committee, abstract, acknowledgments and dedication pages, in the order and form of the WSU Thesis and Dissertation Formatting Guidelines and the WSU ETD example (2024).
- `latex/chapters/` has one file per chapter. `latex/supplement/` has the supporting information.
- `latex/references.bib` was exported from the Zotero citations in the Word draft. Keys follow `authorYEARword`.
- Figures are read from `figures/dissertation/`, with `.pdf` taken before `.png`.
- `fonts/` holds New Computer Modern Book and its math font (GUST Font License), used for text and math, and FiraCode Nerd Font Mono (SIL Open Font License), used for code.

## Formatting choices

- Margins 1 in top and bottom and 1.4 in at the sides (a 5.7 in measure, about 80 characters to the line; WSU asks for 45 to 90), 11 pt type, line stretch 1.15 (142 % of the point size; WSU asks 120 to 145 % for LaTeX), page numbers centered 0.5 in from the bottom edge, roman numerals through the dedication.
- Text in New Computer Modern Book with New Computer Modern Math Book. `notes/font-demo/font-demo.pdf` and `cm-compare.pdf` compare the alternatives; the swap is two lines in `preamble.tex`.
- Chapters open with a spaced small-capital "Chapter", a large numeral, the title in spaced small capitals and a short rule. Sections are in spaced small capitals, subsections in bold, subsubsections in italic. Captions are single-spaced with the label in spaced small capitals.
- Floats go to page tops or float pages and never rise above the heading of their own section (placeins). A figure that opens its section sits in the source right after the heading with `[htp]`, so it lands under the heading when it fits there.
- Display equations are numbered by chapter, (2.3), and S1, S2 in the supplement.
- Cross-references use `\cref{}` (`\Cref{}` at the start of a sentence): Fig. 4.4, Table 4.1, Eq. (2.3), Chapter 4, Sec. 3.5. Panels follow directly, `\cref{fig:4.4}a`. References into the supplement are plain text through `\suppfig{5}`, `\supptab{3}` and `\suppsec{1}`, since separate PDFs cannot link to each other.
- Quantities use siunitx: `\qty{283.7}{eV}`, `\qty{192.7(4)}{\angstrom}`, `\ang{54.7}`. Numeric table columns are siunitx `S` columns aligned on the decimal point.
- The bibliography uses the biblatex-phys style (AIP and APS conventions) with back-references.
- The main text carries a running head, the chapter title in spaced small capitals, 0.7 in from the top edge (WSU exempts running heads from the 1 in margin). Chapter-opening pages, the front matter and the supplement have page numbers only.
- Code listings use the `codeblock` environment (FiraCode, black, a rule on the left); `\code{}` sets a command inside a sentence. WSU requires black text outside figures and tables, so there is no syntax colouring.
- Links are black, as WSU requires. Every figure, table, section and citation reference is a link, the PDF has numbered bookmarks, and each reference in the bibliography lists the pages that cite it as links back into the text.

## Figures

34 of the 51 figures in the dissertation and supplement are vector PDFs. The rest are the originals at their full saved resolution, because no vector version exists. Figures 4.1, 4.2 and 4.4 and S1, S3 to S5, S7, S9, S10 and S13 come from PNGs saved by the notebooks in `refl-analysis/notebooks/`, and Figure 5.1 is `fig4.1_ML-DFT.png`. Rerunning the current `v2/SI9` and `v2/SI11` notebooks with PDF output gives figures that differ from the ones in the dissertation, so those were not swapped in. Figures 3.3, 3.11, 6.1 and 6.7 are a photograph or screenshots. S6 and S11 are still the Word copies in `word-export/`, because the notebook versions differ from what the Word draft shows.

## Origin

Converted on 2026-11-22 from `word/heilman-dissertation-final.docx` using pandoc 3.9 and the scripts in `../src/latex-conversion/`. Those scripts were run once; rerunning them overwrites any edits made here.

## Known cleanup

- 19 captions (Chapters 3, 4 and 5 and the supplement) contained equations that Word stored as plain text. Each is marked `% TODO caption contains equations`.
- Chapter 4 cited subsections of the published SI ("Sec. 3.1", "Sec. 5.4"); the supplement has only sections S1 to S5, so those references now point to the section ("Sec. S3", "Sec. S5").
- Chapter 4 cites "Fig. S13a" for the beta-ZnPc unit cell; the unit cells are in Fig. S12 and S13 is the Fisher analysis, so that reference likely should read S12a.
- WSU asks for the full citation (published) or the statement "Prepared for submission to an academic journal." on the first page of each manuscript chapter. Chapters 5 and 6 carry the statement. Chapter 4 still reads "In review at an academic journal" and needs its citation.
