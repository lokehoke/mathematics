# Book publication and build

This file supersedes the parent instructions about publishing `book/references/` and the locations of build reports and olympiad source metadata.

Publish the manuscript, canonical task data, artwork, fonts and the scripts required by `python3 book/tools/build_book.py`. Keep the rendered reading copy in `rendered/`. Preserve the existing mathematics, tasks, stable UIDs and illustration placement when changing the repository layout.

Do not commit working review reports, exam downloads or text extractions, archive catalogs, one-off review scripts, or generated JSON copies of the assembled manuscript. `book/references/` remains local and ignored. Current build reports go to `book/.work/reports/`, also ignored. The JSON files named `review-*.json` and `exam-*.json` inside `book/source/data/` contain manuscript text and exercises used by the assembler; they are source material, so preserve them.

`book/source/data/olympiad-sources.json` contains only citation metadata for the problems printed in the book. The full local source registry and archived documents are not needed to build the book. Do not remove source labels or primary-source links from the exercises.

The build dependency chain is `build_book.py`, `make_symbols.py`, `assemble_book.py`, `restructure_book.py`, `exam_style.py`, `integrate_deep_review.py`, `verify_book_layout.py`, `publish_book.py` and `restore_pdf_destinations.py`. `book/tools/.gitignore` explicitly allows these scripts. Preserve their dependencies when cleaning publication files. Use this pipeline for validation; the parent instructions about edition-specific review commands refer to local working scripts, which are not publication dependencies.

After changing the build or its paths, verify generation in a clean directory containing only tracked files. A repository-only cleanup must leave the generated LaTeX and the existing reading PDF unchanged. Preserve local files when excluding them from Git.
