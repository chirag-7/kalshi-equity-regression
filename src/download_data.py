"""Download public inputs without API keys. Run from any directory."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw"
BASE = "https://external-api.kalshi.com/trade-api/v2"


def get_json(url):
    return json.loads(get_bytes(url))


def get_bytes(url):
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 academic-course-project"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == 4:
                raise
            time.sleep(2 ** attempt)


def candle_url(ticker, series, start_ts, end_ts, interval, archived=True):
    if interval not in (1, 60, 1440):
        raise ValueError("Kalshi supports 1, 60 or 1440 minutes")
    route = f"/historical/markets/{ticker}/candlesticks" if archived else f"/series/{series}/markets/{ticker}/candlesticks"
    query = urllib.parse.urlencode(dict(start_ts=start_ts, end_ts=end_ts, period_interval=interval))
    return BASE + route + "?" + query


def download_candles(ticker, series, start_ts, end_ts, interval):
    """Route by the published cutoff and split requests below 5,000 periods.

    Missing candles remain missing: no conversion of an inactive minute into
    a newly observed trade. Overlapping boundary candles are deduplicated.
    """
    cutoff = get_json(BASE + "/historical/cutoff")
    market_cutoff = cutoff.get("market_settled_ts")
    if not market_cutoff:
        raise ValueError(f"Unexpected historical-cutoff schema: {list(cutoff)}")
    cut = datetime.fromisoformat(market_cutoff.replace("Z", "+00:00")).timestamp()
    # For the sample this is an archived market. For arbitrary tickers inspect
    # metadata from both tiers rather than infer status from the requested date.
    try:
        meta = get_json(BASE + f"/markets/{ticker}")["market"]
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise
        meta = get_json(BASE + f"/historical/markets/{ticker}")["market"]
    settled = meta.get("settlement_ts")
    archived = bool(settled and datetime.fromisoformat(settled.replace("Z", "+00:00")).timestamp() < cut)
    rows = {}
    step = 4990 * interval * 60
    for lo in range(start_ts, end_ts, step):
        hi = min(lo + step, end_ts)
        data = get_json(candle_url(ticker, series, lo, hi, interval, archived))
        for row in data.get("candlesticks", []):
            rows[row["end_period_ts"]] = row
        time.sleep(.15)
    return {"ticker": ticker, "candlesticks": [rows[t] for t in sorted(rows)]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--intraday-only", action="store_true")
    args = parser.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    source = "https://kalshi-and-the-rise-of-macro-markets.s3.amazonaws.com"
    sources = {
        "daily_moments_fed_levels.csv": source + "/daily_moments_data/daily_moments_fed_levels.csv",
        "fama_french_daily.zip": "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_daily_CSV.zip",
        "fred_daily.zip": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS2,DGS10,VIXCLS&cosd=2021-12-01&coed=2026-11-03",
    }
    for ticker in ["IWM", "SPY"]:
        sources[ticker.lower() + "_daily.json"] = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?period1=1638316800&period2=1793743200&interval=1d&events=div%2Csplits"
    log = []
    if not args.intraday_only:
        for name, url in sources.items():
            payload = get_bytes(url)
            (RAW / name).write_bytes(payload)
            log.append(dict(file=name, url=url, sha256=hashlib.sha256(payload).hexdigest()))
            print("Downloaded", name, flush=True)
    start = int(datetime(2023, 6, 13, tzinfo=timezone.utc).timestamp())
    for interval in (1, 60):
        obj = download_candles("FED-23JUN-T5.25", "FED", start, start + 86400, interval)
        name = f"kalshi_{interval}m_example.json"
        payload = (json.dumps(obj, indent=2) + "\n").encode()
        (RAW / name).write_bytes(payload)
        log.append(dict(file=name, interval_minutes=interval, candles=len(obj["candlesticks"]), sha256=hashlib.sha256(payload).hexdigest()))
        print("Downloaded", name, len(obj["candlesticks"]), "candles", flush=True)
    (ROOT / "data/metadata/latest_download.json").write_text(json.dumps({"retrieved_at_utc": datetime.now(timezone.utc).isoformat(), "files": log}, indent=2))


if __name__ == "__main__":
    main()
