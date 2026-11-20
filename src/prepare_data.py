"""Build a transparent EDA panel, not a synchronized estimation sample."""
from pathlib import Path
import io
import json
import re
import zipfile
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw"
PROCESSED = ROOT / "data/processed"
END = "2026-09-30"


def prices(ticker):
    chart = json.loads((RAW / f"{ticker.lower()}_daily.json").read_text())["chart"]["result"][0]
    dates = pd.to_datetime(chart["timestamp"], unit="s", utc=True).strftime("%Y-%m-%d")
    return pd.Series(chart["indicators"]["adjclose"][0]["adjclose"], index=dates, name=ticker).dropna()


def fred():
    path = RAW / "fred_daily.zip"
    raw = path.read_bytes()
    if raw.startswith(b"PK"):
        frames = []
        with zipfile.ZipFile(path) as archive:
            for name in archive.namelist():
                if name.endswith(".csv"):
                    f = pd.read_csv(io.BytesIO(archive.read(name)), na_values=".").set_index("observation_date")
                    frames.append(f)
        return pd.concat(frames, axis=1).sort_index()
    return pd.read_csv(path, na_values=".").set_index("observation_date")


def factors():
    with zipfile.ZipFile(RAW / "fama_french_daily.zip") as archive:
        text = archive.read(archive.namelist()[0]).decode("utf-8-sig")
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(",Mkt-RF"))
    lines = [lines[start]] + [line for line in lines[start + 1:] if re.match(r"^\d{8},", line)]
    f = pd.read_csv(io.StringIO("\n".join(lines)))
    f.index = pd.to_datetime(f.iloc[:, 0].astype(str), format="%Y%m%d").dt.strftime("%Y-%m-%d")
    return f.drop(columns=f.columns[0]).astype(float)


def parse_candles(path, interval):
    data = json.loads(path.read_text())
    out = []
    for c in data["candlesticks"]:
        def val(block, key):
            v = c.get(block, {}).get(key + "_dollars", c.get(block, {}).get(key))
            return float(v) if v is not None else np.nan
        volume = float(c.get("volume_fp", c.get("volume", 0)))
        out.append(dict(ticker=data["ticker"], interval_minutes=interval,
                        end_period_ts=c["end_period_ts"], price=val("price", "close"),
                        yes_bid=val("yes_bid", "close"), yes_ask=val("yes_ask", "close"),
                        volume=volume))
    frame = pd.DataFrame(out).drop_duplicates("end_period_ts").sort_values("end_period_ts")
    frame["time_utc"] = pd.to_datetime(frame.end_period_ts, unit="s", utc=True)
    frame["time_et"] = frame.time_utc.dt.tz_convert("America/New_York")
    frame["has_trade"] = (frame.volume > 0) & frame.price.notna()
    return frame


def main():
    PROCESSED.mkdir(parents=True, exist_ok=True)
    px = pd.concat([prices("IWM"), prices("SPY")], axis=1).dropna().sort_index()
    returns = px.pct_change(fill_method=None) * 100
    yields = fred()
    ff = factors()
    yields.loc["2021-12-01":"2026-11-03"].to_csv(PROCESSED / "treasury_vix_daily.csv", index_label="date")
    ff.loc["2021-12-01":END].to_csv(PROCESSED / "equity_factors_daily.csv", index_label="date")
    calendar = json.loads((ROOT / "config/event_calendar.json").read_text())
    meetings = sorted(calendar["fomc_decision_dates"])
    cpi = set(calendar["cpi_release_dates"])
    moments = pd.read_csv(RAW / "daily_moments_fed_levels.csv")
    assert not moments.duplicated(["date", "contract_preamble"]).any()
    by_key = moments.set_index(["date", "contract_preamble"])
    month_map = {v: i + 1 for i, v in enumerate(["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"])}
    targets = {}
    for event in moments.contract_preamble.unique():
        suffix = event.split("-")[1]
        year_month = f"20{suffix[:2]}-{month_map[suffix[2:]]:02}"
        found = [d for d in meetings if d.startswith(year_month)]
        if len(found) == 1:
            targets[found[0]] = event
    rows = []
    exclusions = {}
    def exclude(reason):
        exclusions[reason] = exclusions.get(reason, 0) + 1
    for previous, day in zip(px.index, px.index[1:]):
        if day > END:
            continue
        if day in meetings:
            exclude("FOMC decision day")
            continue
        future = [m for m in meetings if m > day]
        meeting = future[0] if future else None
        event = targets.get(meeting)
        if event is None or (previous, event) not in by_key.index or (day, event) not in by_key.index:
            exclude("Missing same meeting pair")
            continue
        conventional = [yields.at[d, k] if d in yields.index and k in yields else np.nan for d in (previous, day) for k in ("DGS2", "DGS10", "VIXCLS")]
        if day not in ff.index or not np.isfinite(conventional).all():
            exclude("Missing conventional input")
            continue
        a, b = by_key.loc[(previous, event)], by_key.loc[(day, event)]
        rows.append(dict(date=day, previous_equity_date=previous, event=event, meeting_date=meeting,
            days_to_meeting=(pd.Timestamp(meeting) - pd.Timestamp(day)).days,
            iwm_return_pct=returns.at[day, "IWM"], spy_return_pct=returns.at[day, "SPY"],
            relative_return_pp=returns.at[day, "IWM"] - returns.at[day, "SPY"],
            market_excess_pct=ff.at[day, "Mkt-RF"],
            yield2_change_bps=100*(yields.at[day, "DGS2"] - yields.at[previous, "DGS2"]),
            vix_change_points=yields.at[day, "VIXCLS"] - yields.at[previous, "VIXCLS"],
            kalshi_mean_rate_pct=b["mean"], kalshi_easing_bps=100*(a["mean"] - b["mean"]),
            cpi_day=int(day in cpi), volume_today=b["daily_volume"], volume_previous=a["daily_volume"],
            timestamp_aligned=False))
    panel = pd.DataFrame(rows)
    assert not panel.date.duplicated().any()
    assert np.isfinite(panel.select_dtypes(include=np.number)).all().all()
    assert (pd.to_datetime(panel.meeting_date) > pd.to_datetime(panel.date)).all()
    assert np.allclose(panel.relative_return_pp, panel.iwm_return_pct - panel.spy_return_pct)
    panel.to_csv(PROCESSED / "daily_eda_candidate.csv", index=False)
    px.loc[:END].to_csv(PROCESSED / "etf_adjusted_prices.csv", index_label="date")
    for interval in (1, 60):
        parse_candles(RAW / f"kalshi_{interval}m_example.json", interval).to_csv(PROCESSED / f"kalshi_{interval}m_example.csv", index=False)
    summary = dict(rows=len(panel), first=panel.date.min(), last=panel.date.max(),
                   meeting_targets=int(panel.event.nunique()), cpi_days=int(panel.cpi_day.sum()),
                   non_cpi_days=int((panel.cpi_day == 0).sum()),
                   nonzero_revisions=int((panel.kalshi_easing_bps.abs() > 1e-8).sum()),
                   both_days_positive_volume=int(((panel.volume_today > 0) & (panel.volume_previous > 0)).sum()),
                   raw_moment_rows=len(moments), raw_moment_events=int(moments.contract_preamble.nunique()),
                   raw_moment_first=moments.date.min(), raw_moment_last=moments.date.max(),
                   exclusions=exclusions, status="Preliminary UTC daily EDA; not a synchronized regression sample")
    (ROOT / "data/metadata/sample_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
