# Technical architecture

```text
policyholders.csv  +  buyers.csv
           |              |
           +-- credit_limits.csv --+
                                     +-- invoices.csv <-- payments.csv (dated)
                                                  |
                                    Python ETL and validation
                                      |                |
                                      v                v
                                    SQLite       rejected anomalies
                                      |
                           As-of snapshots (2026-10-31)
                                      |
                    +-----------------+------------------+
                    |                 |                  |
                Portfolio KPIs    Alert rules       Scenario grid
                    |                 |                  |
                    +-----------------+------------------+
                                      |
                             Dashboard + BI exports
```

- Buyer and insured supplier are distinct entities. A credit-limit relationship binds an insured supplier to a buyer.
- Dated payments allow invoice outstanding amounts to be recalculated at an as-of date without using future receipts.
- Monetary amounts are stored in integer Moroccan dirhams in the simulation to avoid float rounding.
- The HTML demonstration contains precomputed data and works offline. GitHub Pages hosts the generated page.
- See [methodology](METHODOLOGY.md) for alert thresholds, simulation assumptions and known limitations.
