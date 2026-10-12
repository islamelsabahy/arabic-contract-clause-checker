# Changelog

## 0.2.0
- Browser version (`docs/`, GitHub Pages): paste, drop or open a .txt contract, pick sale or lease, get findings with excerpts and fixes, export a PDF report (print dialog) or copy it. Arabic/English UI; the text never leaves the browser.
- Normalisation now removes zero-width and bidi control marks (RLM/LRM/embedding marks, BOM) that Word/PDF copy-paste leaves inside Arabic words; they used to hide clauses and risks.
- Python and JS are checked against each other: rules and normaliser tables are generated into `docs/rules.js` by `scripts/build_web_data.py`; `node tests/test_checker.js` replays Python-generated vectors in CI; a unit test fails if generated files go stale.

## 0.1.0
- First release: sale and lease checklists, risky-wording rules, Arabic normalisation, English/Arabic reports, JSON output.
