# Architecture technique — Stage 1

```text
     policyholders.csv            buyers.csv
              │                       │
              └───────┬───────────────┘
                      ▼
               credit_limits.csv
                      │
                      ▼
                 invoices.csv  ◄── payments.csv (dated cash events)
                      │
                      ▼
           Python import + data quality rules
                      │                    └──► rejected_rows / anomalies.csv
                      ▼
          SQLite (foreign keys, constraints)
                      │
                      ▼
             Historical snapshot at T
                      │
           ┌──────────┴──────────┐
           ▼                     ▼
  invoices_snapshot.csv   credit_limits_snapshot.csv
           └──────────┬──────────┘
                      ▼
                   kpis.json

Stages 2–4: offline interactive portfolio overview, explainable alert center and Python precomputed stress scenario lab.
Stage 5: Power BI-ready CSV extracts and GitHub Pages demo.
```

Amounts are stored as integer Moroccan dirhams (MAD) to avoid float rounding errors in the demo. The project is independent of Power BI for reproducibility. The insured seller (`policyholder`) is *not* the same role as the buyer/debtor (`buyer`).
