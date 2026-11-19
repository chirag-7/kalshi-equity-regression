"""Reproduce every table and all four figures used in the description."""
from pathlib import Path
import json
import os
os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[1] / "work/matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "reports/figures"
TABLE = ROOT / "reports/tables"
LABELS = {
    "relative_return_pp": ("IWM minus SPY return", "percentage points"),
    "kalshi_easing_bps": ("Kalshi easing revision", "basis points"),
    "market_excess_pct": ("Market excess return", "percent"),
    "yield2_change_bps": ("Change in 2 year yield", "basis points"),
    "vix_change_points": ("Change in VIX", "index points"),
}


def save(fig, name):
    fig.savefig(FIG / (name + ".png"), dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    TABLE.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
        "axes.spines.right": False, "axes.labelcolor": "#222222", "text.color": "#222222",
        "axes.titleweight": "bold", "axes.titlesize": 13, "grid.alpha": .2})
    panel = pd.read_csv(ROOT / "data/processed/daily_eda_candidate.csv")
    stats = panel[list(LABELS)].describe(percentiles=[.05, .5, .95]).T
    stats = stats[["count", "mean", "std", "5%", "50%", "95%", "min", "max"]]
    stats.index.name = "variable"
    stats.to_csv(TABLE / "descriptive_statistics.csv")
    groups = panel.assign(abs_revision_bps=panel.kalshi_easing_bps.abs()).groupby("cpi_day").agg(
        n=("date", "size"), mean_abs_revision_bps=("abs_revision_bps", "mean"),
        median_abs_revision_bps=("abs_revision_bps", "median"),
        p95_abs_revision_bps=("abs_revision_bps", lambda s: s.quantile(.95)),
        return_sd_pp=("relative_return_pp", "std"))
    groups.to_csv(TABLE / "cpi_comparison.csv")
    panel[list(LABELS)].corr().to_csv(TABLE / "candidate_correlations.csv")
    px = pd.read_csv(ROOT / "data/processed/etf_adjusted_prices.csv", index_col="date", parse_dates=True)
    fig, ax = plt.subplots(figsize=(8.8, 3.7))
    for ticker, color in [("IWM", "#267481"), ("SPY", "#c66b38")]:
        ax.plot(px.index, 100*px[ticker]/px[ticker].iloc[0], label=ticker, lw=1.6, color=color)
    ax.set(title="Small and large cap returns follow different paths", ylabel="Adjusted price index  |  first day = 100")
    ax.grid(axis="y");ax.legend(frameon=False, ncol=2)
    ax.xaxis.set_major_locator(mdates.YearLocator());ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    fig.tight_layout();save(fig, "01_equity_performance")

    fig, ax = plt.subplots(figsize=(8.8, 3.7))
    values = [panel.loc[panel.cpi_day == d, "kalshi_easing_bps"].abs().to_numpy() for d in [0, 1]]
    box = ax.boxplot(values, tick_labels=[f"Other days  (n={len(values[0]):,})", f"CPI days  (n={len(values[1]):,})"],
                     patch_artist=True, showfliers=False, widths=.42, medianprops={"color": "black", "linewidth": 1.5})
    for patch, color in zip(box["boxes"], ["#c6dfe2", "#f0c4a7"]):patch.set_facecolor(color)
    rng = np.random.default_rng(4205)
    for pos, val, color in zip([1,2], values, ["#267481", "#c66b38"]):
        ax.scatter(pos+rng.uniform(-.13,.13,len(val)), val, s=11, alpha=.35, color=color)
    ax.set_yscale("symlog", linthresh=1)
    ax.set(title="How much do Kalshi rate expectations move on CPI days?", ylabel="Absolute revision in basis points\nLinear to 1 bp then log scale")
    ax.grid(axis="y");fig.tight_layout();save(fig, "02_cpi_repricing")

    fig, ax = plt.subplots(figsize=(8.8, 3.7))
    scatter = ax.scatter(panel.days_to_meeting, panel.kalshi_easing_bps.abs(),
        c=np.log10(1+panel.volume_today), cmap="viridis", s=19, alpha=.65,
        norm=Normalize(vmin=0, vmax=np.log10(1+panel.volume_today.max())), linewidths=0)
    ax.set_yscale("symlog", linthresh=1)
    ax.set(title="Kalshi revisions by time to meeting and trading volume", xlabel="Calendar days until the target Fed meeting",
        ylabel="Absolute Kalshi revision in basis points\nLinear to 1 bp then log scale")
    cb=fig.colorbar(scatter, ax=ax, pad=.025)
    cb.set_label("Daily volume  |  log10(1 + contracts)")
    ax.grid(axis="y");fig.tight_layout();save(fig, "03_horizon_volume_repricing")

    minute = pd.read_csv(ROOT / "data/processed/kalshi_1m_example.csv")
    minute["time"] = pd.to_datetime(minute.time_utc, utc=True).dt.tz_convert("America/New_York")
    start = pd.Timestamp("2023-06-13 07:00", tz="America/New_York")
    end = pd.Timestamp("2023-06-13 16:00", tz="America/New_York")
    shown = minute[(minute.time >= start) & (minute.time <= end) & minute.has_trade].copy()
    fig, ax = plt.subplots(figsize=(8.8, 3.7))
    ax.scatter(shown.time, 100*shown.price, color="#267481", s=24, zorder=3, label="Minute with a trade")
    release = pd.Timestamp("2023-06-13 08:30", tz="America/New_York")
    ax.axvline(release, color="#c66b38", linestyle="--", lw=1.3, label="CPI release at 8:30 am")
    ax.set(title="A minute level view of the June 2023 Fed contract", ylabel="YES trade price in cents", xlabel="13 June 2023  |  New York time", xlim=(start,end))
    ax.xaxis.set_major_locator(mdates.HourLocator(tz=start.tz))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=start.tz))
    ax.grid(axis="y");ax.legend(frameon=False, loc="best", fontsize=9)
    fig.tight_layout();save(fig, "04_minute_cpi_example")

    insight = {
        "cpi_mean_abs_revision_bps": float(groups.loc[1,"mean_abs_revision_bps"]),
        "other_mean_abs_revision_bps": float(groups.loc[0,"mean_abs_revision_bps"]),
        "cpi_median_abs_revision_bps": float(groups.loc[1,"median_abs_revision_bps"]),
        "other_median_abs_revision_bps": float(groups.loc[0,"median_abs_revision_bps"]),
        "mean_abs_revision_ratio": float(groups.loc[1,"mean_abs_revision_bps"]/groups.loc[0,"mean_abs_revision_bps"]),
        "zero_revision_share": float((panel.kalshi_easing_bps.abs() <= 1e-8).mean()),
        "relative_return_sd_pp": float(panel.relative_return_pp.std()),
        "relative_return_mean_pp": float(panel.relative_return_pp.mean()),
        "relative_return_p05_pp": float(panel.relative_return_pp.quantile(.05)),
        "relative_return_p95_pp": float(panel.relative_return_pp.quantile(.95)),
        "c_yield_correlation": float(panel.kalshi_easing_bps.corr(panel.yield2_change_bps)),
        "iwm_total_return_pct": float(100*(px.IWM.iloc[-1]/px.IWM.iloc[0]-1)),
        "spy_total_return_pct": float(100*(px.SPY.iloc[-1]/px.SPY.iloc[0]-1)),
        "minute_candles_returned": len(minute),
        "minute_trade_bars_returned": int(minute.has_trade.sum()),
        "minute_trade_bars_in_plot": len(shown),
        "minute_plot_min_price_cents": float(100*shown.price.min()),
        "minute_plot_max_price_cents": float(100*shown.price.max()),
        "hourly_candles_returned": len(pd.read_csv(ROOT / "data/processed/kalshi_60m_example.csv")),
    }
    (ROOT / "reports/tables/insights.json").write_text(json.dumps(insight, indent=2)+"\n")
    print(json.dumps(insight, indent=2))


if __name__ == "__main__":
    main()
