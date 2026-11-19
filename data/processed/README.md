# Processed data

`python src/prepare_data.py` writes the candidate daily panel and the minute/hourly examples here. These files are local analysis inputs, excluded from Git.

The daily panel is for preliminary description. Its `kalshi_easing_bps` variable uses the authors' UTC daily series. It is deliberately not named or treated as a final synchronized regression sample. `src/fit_models.py` refuses to fit it until a separately prepared file passes the timing and quote-quality checks documented in `docs/methodology.md`.
