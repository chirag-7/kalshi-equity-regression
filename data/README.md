# Project data

All collected source files and the prepared CSVs are included in this repository. No API key or download command is needed to use the snapshot. On GitHub, open a file and select **Download raw file**. To get everything at once, select **Code → Download ZIP** on the repository homepage.

## Start here

Use [`processed/daily_eda_candidate.csv`](processed/daily_eda_candidate.csv) for the preliminary daily analysis. It contains 1,143 rows from 2 December 2021 to 30 September 2026, with one observation per candidate trading day. The related returns, controls and indicators are already in the same table.

This is the descriptive-analysis dataset used for the project description. Kalshi expectations still use source UTC daily observations rather than synchronized equity-close readings. Every row is marked `timestamp_aligned=False`. It should not be treated as the final regression sample.

## Daily project dataset columns

| Column | Meaning and unit |
| --- | --- |
| `date` | Current trading date |
| `previous_equity_date` | Previous date with both ETF prices; can be several calendar days earlier |
| `event` | Kalshi target meeting identifier |
| `meeting_date` | Official FOMC decision date for that target |
| `days_to_meeting` | Calendar days from the current date to the meeting |
| `iwm_return_pct` | Adjusted IWM return in percent |
| `spy_return_pct` | Adjusted SPY return in percent |
| `relative_return_pp` | IWM minus SPY return, in percentage points; the response Y |
| `market_excess_pct` | Kenneth French market excess return in percent; M |
| `yield2_change_bps` | Change in the 2-year Treasury yield in basis points; T |
| `vix_change_points` | Change in VIX in index points; V |
| `kalshi_mean_rate_pct` | Source expected Fed upper-bound rate for the target meeting, in percent |
| `kalshi_easing_bps` | Previous expected rate minus current expected rate, in basis points, for the same meeting; C |
| `cpi_day` | 1 on an official CPI release day, otherwise 0; D |
| `volume_today` | Source total contract volume for the target meeting on the current UTC date |
| `volume_previous` | Source total contract volume for the target meeting on the previous equity date |
| `timestamp_aligned` | False throughout this preliminary dataset |

For model 4, the interaction is `kalshi_easing_bps * cpi_day`. A positive C means expectations moved toward lower rates. A positive Y means IWM outperformed SPY.

## Other prepared files

| File | Contents |
| --- | --- |
| [ETF adjusted prices](processed/etf_adjusted_prices.csv) | Date, IWM and SPY adjusted price levels from 1 December 2021 to 30 September 2026 |
| [Treasury yields and VIX](processed/treasury_vix_daily.csv) | Date and FRED DGS2, DGS10 and VIXCLS observations over the collected project period; missing source values remain blank |
| [Equity factors](processed/equity_factors_daily.csv) | Date and the French `Mkt-RF`, `SMB`, `HML`, `RMW`, `CMA` and `RF` daily series, in percent |
| [Minute example](processed/kalshi_1m_example.csv) | 70 returned minute candles for FED-23JUN-T5.25 over the requested 13 June 2023 UTC window; 67 contain trades |
| [Hourly example](processed/kalshi_60m_example.csv) | 13 returned hourly candles for the same contract and requested window |

Intraday columns include the contract ticker, interval length in minutes, Unix candle-end timestamp, UTC and New York timestamps, YES trade price, YES bid, YES ask, volume and a `has_trade` flag. Prices are in dollars per $1 payout: 0.20 means 20 cents. A missing candle is not a zero price change. Candle intervals describe the sampling frequency, not continuous trading activity.

## Source downloads and provenance

`raw/` contains the collected daily Kalshi moments and distributions, original IWM and SPY responses, FRED and French ZIP archives, and minute/hourly Kalshi API responses. The source daily collection was obtained on 4 November 2026; the intraday examples were downloaded on 19 November 2026. These are the existing snapshots used for the description, not a new update through today's date.

[`metadata/frozen_snapshot_manifest.json`](metadata/frozen_snapshot_manifest.json) gives source URLs, retrieval dates and hashes. [`metadata/included_data_manifest.json`](metadata/included_data_manifest.json) inventories the data files shipped in this repository. Source definitions and literature are in [the source list](../docs/sources.md); construction and remaining timing work are in [the methodology](../docs/methodology.md).
