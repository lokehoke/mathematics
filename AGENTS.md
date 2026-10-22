# Mathematics workspace

This repository contains a Russian mathematics textbook and an archive of public mathematics olympiad materials.

## Layout

- `sources/book/`: authoritative LaTeX manuscript, fonts and book illustrations.
- `rendered/`: final compiled PDFs for reading.
- `scripts/`: build scripts, figure generation and archive download utilities.
- `olympiads/russia/`, `olympiads/international/`, `olympiads/university/`: downloaded public contest materials.
- `research/`: official source registers, archive indexes and verification reports.

## Book

Keep the agreed title: «Алгебра перед математическим анализом для Насти».
Use proper LaTeX mathematics, term-only underlining, English equivalents for definitions, numbered theorems and readable color illustrations. Match the cover palette (cream paper, navy, muted teal, ochre). Place large, unique watercolor cats inside the normal content area with text wrapping around them, roughly every two or three pages. Keep formulas legible and prevent overlaps with text or page numbers. Preserve existing exercises when adding material. Include answers and proofs for theoretical exercises. Build from `sources/book/main.tex`; put the deliverable in `rendered/`. Inspect rendered pages after layout changes. Do not run the obsolete plain-text-to-LaTeX converter from earlier drafts.

## Olympiad archive

Collect mathematics only. Prefer official contest organizers and official legal publications. Download publicly accessible tasks and published answers/solutions; record their actual year, round, class/age group and source URL. Do not invent missing years or bypass sign-in/paywalls. Preserve documents as published and keep a machine-readable manifest with URL, local path, contest, year/round when known, document type, download status and SHA-256. Separate discovery from successful downloads and report coverage gaps honestly. Distinguish inclusion in a ministry list from the admission rules of a particular university.

## Collaboration

Parallel agents should work in separate contest folders or separate manuscript fragments. Do not overwrite another agent's active manuscript. Integrate reviewed fragments centrally. Commit source and reproducible scripts; exclude LaTeX auxiliary files and temporary render previews. Do not remove existing user files when reorganizing.
