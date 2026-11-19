# Study design

## Research question

Do revisions in Kalshi's expected Fed rate add explanatory information about small-cap returns relative to large-cap returns, beyond market returns, Treasury yields and VIX? Does the association change on CPI release days?

This is a contemporaneous observational study. It does not claim a causal policy effect or a forecast available before the return occurs.

## Variables and four models

For trading day t:

- Y is the adjusted IWM return minus the adjusted SPY return, in percentage points. Each ETF return is 100 times its adjusted price ratio minus 100. An index difference is not a pure size exposure: industries and other characteristics also differ.
- M is the Kenneth French market excess return in percent.
- T is the change in the 2-year Treasury yield in basis points, using DGS2.
- V is the change in VIX in index points, using VIXCLS.
- C is 100 times the previous expected rate minus the current expected rate for the **same next FOMC meeting**. Expected-rate levels are in percent, so C is in basis points. Positive C means an easing revision. One basis point is 0.01 percentage point.
- D is 1 on a BLS CPI release day and 0 otherwise.

The four nested models, always estimated on the same complete sample, are:

1. `Y = a + bM*M + bT*T + bV*V + error`
2. `Y = a + bM*M + bT*T + bV*V + eta*C + error`
3. `Y = a + bM*M + bT*T + bV*V + eta*C + delta*D + error`
4. `Y = a + bM*M + bT*T + bV*V + eta*C + delta*D + lambda*C*D + error`

Model 3 lets the intercept differ on CPI days. Model 4 also lets the Kalshi slope differ: eta on other days and eta + lambda on CPI days. The interaction test is lambda = 0. It is not a test that the return itself is zero. A CPI indicator is not the numerical inflation surprise.

We test eta = 0 when moving from model 1 to 2; delta = 0 from 2 to 3; lambda = 0 from 3 to 4. For model 4, also report a confidence interval for eta + lambda. The added-term tests use clustered uncertainty, rather than an ordinary homoskedastic nested F test. Report changes in adjusted R squared as descriptive fit measures.

## Why these controls

Market return accounts for unequal market exposure that does not cancel when subtracting ETF returns. The 2-year yield is a conventional market measure of near-term rate repricing, making it a demanding benchmark for Kalshi. VIX accounts for changes in expected equity volatility. These are partial associations conditional on the controls; conditioning on yield changes can remove part of the same policy news Kalshi measures. The coefficient is an incremental-information coefficient, not the total effect of monetary policy.

Use the five-factor model only as a sensitivity check. SMB resembles the outcome itself, so including it changes the question to the residual variation left after controlling for a size factor. Add HML, RMW and CMA separately before trying the full five factors. Yield-curve slope and credit spreads are additional sensitivity checks, not a large automatic control set selected for significance.

## Collected daily data and current limits

The frozen 4 November 2026 collection contains 7,657 Kalshi date-target observations from 2 July 2021 to 23 October 2026, covering 52 meeting targets, including contracts beyond the candidate sample. These are derived expectations from the Diercks, Katz and Wright research archive, not observed policy rates. Their threshold-to-distribution procedure and stale trade handling matter.

The preliminary panel has 1,143 dates, 40 target meetings and 54 CPI days from 2 December 2021 through 30 September 2026. The endpoint is fixed by the collected daily French factors. It excludes 39 FOMC decision dates, 15 dates lacking same-target pairs and 14 with missing conventional inputs. These are mutually exclusive exclusions applied in that order in the pipeline. Weekends and holidays do not create return observations. Monday changes compare to Friday for the same meeting.

The research archive uses UTC daily observations and can carry forward old trades. It is appropriate for initial descriptive work, but not yet for the proposed precisely synchronized return regression. Charts 2 and 3 use the source daily construction and are labeled accordingly. They are not coefficient estimates or evidence of causality. The pipeline marks every preliminary row `timestamp_aligned=False`; the estimation script rejects that file.

## How minute and hourly data enter the project

Kalshi's live and historical candle endpoints accept 1, 60 or 1440 minutes. The route depends on the historical cutoff, which can change. A request can cover at most 5,000 periods; the downloader splits longer windows and deduplicates boundaries. On 19 November 2026, direct requests for FED-23JUN-T5.25 over 13 June 2023 UTC returned 70 minute candles and 13 hourly candles. Sixty-seven minute candles contained trades. Figure 4 shows the 56 traded minutes ending between 07:00 and 16:00 New York time. This proves access for that example, not complete intraday coverage for every contract since 2021.

For the core daily regression, hourly candles provide readings at the US equity close (normally 16:00 New York time; use 13:00 on early-close days). Minute/trade data resolve gaps and allow a stricter freshness check. Use actual exchange sessions and daylight-saving-aware timestamps. Do not use a candle ending after the equity cutoff.

Before labeling a panel synchronized:

1. Collect the relevant strikes for the same target meeting at both endpoints. Use the source paper's distribution construction, and document interpolation, monotonicity corrections and tail assumptions. A single threshold price is not an expected rate.
2. Use only information available by the equity close. Record the underlying last trade time and quote age; a candle timestamp alone does not prove that the quote is fresh. Flag absent, crossed, wide or stale quotes. Pre-specify freshness and spread limits after examining coverage, before looking at regression significance. Record retained and excluded counts and repeat with stricter limits.
3. Keep both endpoints on the same contract target. Exclude FOMC decision days in the primary specification. Handle a CPI and FOMC date collision under that same exclusion rule.
4. Merge the equity return, factors, DGS2 and VIX on the appropriate trading date. DGS2 is a daily published yield observation, not a tick-level synchronized Treasury quote.
5. Create `timestamp_aligned` and `quote_quality_passed` audit flags only after these checks, and save the final file separately from the EDA panel.

The minute example is an additional exploratory view around the CPI release. Its price refers to the probability of an upper-bound rate above 5.25% after the 14 June 2023 meeting. A 1-cent move is roughly one probability point, not one basis point of the expected rate. Missing minutes are not zero changes. Prices also reflect trading frictions and risk premia.

An hourly equity-return extension requires hourly IWM, SPY and comparable controls over exactly the same window. Daily DGS2 must not be repeated across hours and interpreted as an intraday yield change. CPI usually arrives at 08:30, before the 09:30 regular equity open, so premarket ETF prices would need a separate liquidity check. This extension is secondary; more bars do not create more independent CPI announcements or Fed meetings.

## Estimation and robustness for the final report

Use OLS with uncertainty clustered by target meeting cycle; report the number of cycles. About 40 clusters limits precision, especially for interaction terms. Inspect residuals, serial dependence, heteroskedasticity, VIFs, leverage and Cook's distance. Compare with HAC uncertainty and, if practical, a wild cluster bootstrap. Use Huber regression to check coefficient sensitivity to extreme returns; its default standard errors do not correct serial dependence.

Repeat after leaving out one meeting cycle at a time and after tightening liquidity filters. Compare an upward versus downward repricing interaction only as a pre-specified secondary question. Keep chronological validation as a stability check, using earlier data for estimation and later complete meeting cycles for validation. Same-day information in the test period does not make this a tradable ahead-of-time forecast. Do not randomly split minute bars.

No regressions have been fitted for this preliminary description. An insignificant incremental Kalshi coefficient or interaction is a valid eventual result.

## Economic motivation

Gertler and Gilchrist (1994) find a disproportionate contraction among small manufacturing firms following tightening. Ehrmann and Fratzscher (2004) find heterogeneous stock responses related to financial constraints, including firm size within the S&P 500. These findings motivate studying relative size exposure; they do not establish that IWM minus SPY is a direct measure of borrowing costs. Firm-level debt data would be needed to test that mechanism directly.

References and data links are in [sources.md](sources.md).
