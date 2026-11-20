# Raw data

The collected source files are included here. Download individual files using GitHub's **Download raw file** button, or choose **Code → Download ZIP** on the repository homepage. No download script is required. Source URLs, original retrieval dates and checksums are in `../metadata/`.

The report uses the daily snapshot collected on 4 November 2026 and the intraday examples downloaded on 19 November 2026. Live downloads can change as sources revise or extend their files. Check their sample counts against the saved snapshot metadata before replacing the report.

The ZIP files preserve the original FRED and Kenneth French downloads. Convenient CSV versions of the relevant daily series are in `../processed/`. `candidate_dates.json` records the original feasibility audit and is not a final estimation sample. Run `python src/download_data.py` only if you want to retrieve the sources again.
