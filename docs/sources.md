# Sources

## Data and construction

- Diercks, Katz and Wright, *Kalshi and the Rise of Macro Markets*: [Federal Reserve paper](https://www.federalreserve.gov/econres/feds/files/2026010pap.pdf), [public code](https://github.com/jdkatz21/Prediction_Markets_Public), [data site](https://jdkatz21.github.io/Prediction_Markets_Public/). Consult their code for probability-distribution construction and forward filling.
- [Kalshi historical candles](https://docs.kalshi.com/api-reference/historical/get-historical-market-candlesticks), [live candles](https://docs.kalshi.com/api-reference/market/get-market-candlesticks), [historical data guide](https://docs.kalshi.com/getting_started/historical_data). Intraday access checked directly on 19 November 2026.
- [FRED DGS2](https://fred.stlouisfed.org/series/DGS2), [VIXCLS](https://fred.stlouisfed.org/series/VIXCLS) and [DGS10](https://fred.stlouisfed.org/series/DGS10). The 10-year yield is retained only for an optional curve-slope check.
- [Kenneth French data library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html). Only market excess return enters the primary four models.
- Yahoo Finance adjusted daily price history: [IWM](https://finance.yahoo.com/quote/IWM/history/), [SPY](https://finance.yahoo.com/quote/SPY/history/). Adjusted prices account for distributions and splits according to the provider.
- [BLS CPI archive](https://www.bls.gov/bls/news-release/cpi.htm), including the [13 June 2023 release](https://www.bls.gov/news.release/archives/cpi_06132023.htm).
- [Official FOMC calendar](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm). Use decision dates, not the research archive's last observed trade date labeled expiry.

## Motivation

- Gertler and Gilchrist (1994), *Monetary Policy, Business Cycles, and the Behavior of Small Manufacturing Firms*, Quarterly Journal of Economics 109(2), 309-340. [Published paper](https://doi.org/10.2307/2118465).
- Ehrmann and Fratzscher (2004), *Taking Stock: Monetary Policy Transmission to Equity Markets*. [ECB working paper 354](https://www.ecb.europa.eu/pub/pdf/scpwps/ecbwp354.pdf).
- Bernanke and Gertler (1995), *Inside the Black Box: The Credit Channel of Monetary Policy Transmission*. [NBER version](https://www.nber.org/papers/w5146).
- Guo (2004), *Stock Prices, Firm Size, and Changes in the Federal Funds Rate Target*. The size effect depends on economic conditions. [Federal Reserve working paper version](https://files.stlouisfed.org/files/htdocs/wp/2002/2002-004.pdf).

The course brief supplied by the student requires a team list, collected-data description, descriptive statistics, at least four plots with one showing three dimensions, comments on the plots and analysis objectives. The project description is due 20 November 2026. The instructor's PDF is not redistributed in this repository.
