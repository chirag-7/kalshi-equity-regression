# Processed data

Ready-to-open CSVs are included here. Download them individually from GitHub, or download the repository ZIP. No API call or preparation command is needed to use the saved files. See [the data guide](../README.md) for column definitions and units.

`python src/prepare_data.py` can regenerate these files from the included source downloads. It also exports the Treasury/VIX series and equity factors as regular CSVs, so readers do not need to unpack or parse the source ZIP archives.

The daily panel is for preliminary description. Its `kalshi_easing_bps` variable uses the authors' UTC daily series. It is deliberately not named or treated as a final synchronized regression sample. `src/fit_models.py` refuses to fit it until a separately prepared file passes the timing and quote-quality checks documented in `docs/methodology.md`.
