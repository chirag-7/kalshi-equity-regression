"""Four pre-specified regressions, enabled only for a synchronized panel.

No fitted results from the preliminary UTC daily panel are in this submission.
"""
from pathlib import Path
import argparse
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
BASE = ["market_excess_pct", "yield2_change_bps", "vix_change_points"]
SPECS = [BASE, BASE+["kalshi_easing_bps"], BASE+["kalshi_easing_bps", "cpi_day"],
         BASE+["kalshi_easing_bps", "cpi_day", "kalshi_cpi_interaction"]]


def validate(panel):
    flags = ["timestamp_aligned", "quote_quality_passed"]
    for flag in flags:
        if flag not in panel or not panel[flag].astype(str).str.lower().isin(["true", "1"]).all():
            raise ValueError(f"Cannot estimate: every observation must pass {flag}. See docs/methodology.md.")
    required = BASE+["date", "event", "relative_return_pp", "kalshi_easing_bps", "cpi_day"]
    if any(k not in panel for k in required):
        raise ValueError("Missing required model variables")
    if panel.date.duplicated().any():
        raise ValueError("Daily panel has duplicate dates")
    if panel[required].isna().any().any():
        raise ValueError("Use one complete common sample for all four models")
    if not panel.cpi_day.isin([0,1]).all():
        raise ValueError("cpi_day must equal zero or one")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=ROOT/"data/processed/daily_eda_candidate.csv")
    args = parser.parse_args()
    panel = pd.read_csv(args.input).sort_values("date")
    validate(panel)
    panel["kalshi_cpi_interaction"] = panel.kalshi_easing_bps * panel.cpi_day
    out = ROOT/"reports/model_results"
    out.mkdir(exist_ok=True)
    fits=[]
    for i, columns in enumerate(SPECS, 1):
        x = sm.add_constant(panel[columns], has_constant="add")
        if np.linalg.matrix_rank(x) != x.shape[1]:
            raise ValueError(f"Model {i} has a rank-deficient design matrix")
        fit = sm.OLS(panel.relative_return_pp,x).fit(cov_type="cluster",cov_kwds={"groups":panel.event,"use_correction":True},use_t=True)
        fits.append(fit)
        (out/f"model_{i}.txt").write_text(fit.summary().as_text())
        pd.DataFrame({"coefficient":fit.params,"standard_error":fit.bse,"p_value":fit.pvalues,
                      "ci_low":fit.conf_int()[0],"ci_high":fit.conf_int()[1]}).to_csv(out/f"model_{i}_coefficients.csv")
    tests = {}
    for index, name in [(1,"kalshi_easing_bps"),(2,"cpi_day"),(3,"kalshi_cpi_interaction")]:
        tests[f"model_{index+1}_added_term"] = str(fits[index].t_test(name+" = 0"))
    tests["model_4_cpi_slope"] = str(fits[3].t_test("kalshi_easing_bps + kalshi_cpi_interaction = 0"))
    (out/"robust_nested_tests.json").write_text(json.dumps(tests,indent=2))
    # Descriptive robustness only: retain OLS with clustered uncertainty as the
    # main inference. Huber's default SE is not a correction for time dependence.
    robust = sm.RLM(panel.relative_return_pp,sm.add_constant(panel[SPECS[3]],has_constant="add"),M=sm.robust.norms.HuberT()).fit()
    robust.params.to_csv(out/"huber_sensitivity_coefficients.csv")
    print("Saved the four models and cluster-robust term tests to",out)


if __name__ == "__main__":
    main()
