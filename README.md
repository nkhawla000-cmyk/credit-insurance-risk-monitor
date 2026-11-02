# Credit Insurance Risk Monitor

**Trade Credit Insurance · Portfolio Analytics · Explainable Early Warning · Scenario-Based Sensitivity Analysis**

![Executive overview of the dashboard](assets/overview.png)

> **Academic portfolio project — 100% synthetic B2B data.** All buyer IDs, payments, invoices and credit limits are simulated. Results are not estimates of the Moroccan market, and no real underwriting or insurance decisions are automated.

### Try the interactive demo

🚀 **[Explore the Live Interactive Dashboard](https://nkhawla000-cmyk.github.io/credit-insurance-risk-monitor/)**

The browser-based dashboard has three interactive modules. No sign-in or Python installation is required to try the published demonstration.

| Executive Risk Overview | Explainable Early Warning | Scenario & Sensitivity Analysis |
|---|---|---|
| ![Portfolio overview](assets/overview.png) | ![Risk alerts](assets/early_warning.png) | ![Scenario analysis](assets/stress_scenarios.png) |

### Business problem and solution

In trade credit insurance, the insured supplier and the buyer/debtor are distinct parties. Monitoring can involve outstanding receivables, overdue invoices, buyer concentration, credit limits and exceptions requiring manual review.

This educational prototype connects those signals through a reproducible data pipeline and a decision-support dashboard:

- **Portfolio monitoring:** receivables, aging buckets, sector exposures, limit utilization and buyer concentration.
- **Explainable alerts:** rule-based priorities with human-readable reasons and suggested verification steps.
- **Sensitivity analysis:** 30 hypothetical combinations of delayed invoice aging and reduced simulated limits, with before/after comparisons and no changes to the underlying cash events.
- **Data quality:** import checks and quarantining of invalid records; as-of calculations based on dated payments.

### Reproducible demonstration snapshot — 31 October 2026

| Metric | Synthetic result |
|---|---:|
| Insured suppliers | 8 |
| Buyers | 80 |
| Credit-limit relationships | 140 |
| Valid invoices | 840 |
| Outstanding receivables | 22.87 million MAD |
| Overdue receivables | 18.26 million MAD |
| Credit-limit excess | 3.43 million MAD |
| Flagged credit-limit relationships | 119 / 140 |
| Import-quality rejections | 4 |

**Interpretation:** this dataset intentionally represents a highly stressed portfolio: about 80% of outstanding receivables are overdue and 119/140 limit relationships trigger rule-based alerts. It is **not a representative real-world portfolio**, and the alert rate is not a default rate.

### Architecture

```text
Synthetic CSV files
        |
        v
Python ETL + data-quality validation --> quarantined records
        |
        v
SQLite + dated payment events --> as-of invoice / limit snapshots
        |
        +--> Portfolio KPIs and aging analytics
        +--> Explainable rule-based alerts
        +--> 30 precomputed sensitivity scenarios
        +--> Offline interactive HTML dashboard (GitHub Pages)
        +--> CSV exports and example DAX measures for Power BI
```

### Run locally

Requires **Python 3.10+**, using only the standard library.

```bash
python3 -m src.generate
python3 run.py --as-of 2026-10-31
python3 export_powerbi.py
python3 build_dashboard.py
python3 -m unittest discover -s tests -v
open dashboard/index.html  # macOS
```

The test suite covers import consistency, historical payment logic, portfolio reconciliation, alerts, dashboard data and sensitivity scenarios. At the verified release, **41 automated tests pass**.

### Files and documentation

- `src/` — synthetic dataset generation, ETL, calculations, alert rules, scenarios and BI exports.
- `data/` — synthetic input CSV files.
- `outputs/` — reproducible, generated snapshots (SQLite database is not committed).
- `dashboard/` — source template and a generated, standalone HTML demo.
- `tests/` — Python unittest suite.
- `assets/` — screenshots of dashboard views.
- `powerbi/datasets/` — CSV exports for BI reporting; `powerbi/mesures.dax` contains example measures.
- [Methodology, assumptions and limitations](docs/METHODOLOGY.md) — definitions and interpretation of the simulated results.
- [Technical architecture](docs/ARCHITECTURE.md) — component and data flow.
- [Power BI setup guide](docs/POWER_BI_FR.md) — guidance for Mac and Windows.

**Power BI status:** CSV exports and DAX examples are provided; no `.pbix` file or published Power BI report is claimed.

### Scope and limitations

- The priority indicator is a transparent **heuristic**, not a calibrated probability of default, a validated credit score or an underwriting decision.
- The what-if module measures **sensitivity of overdue exposure, limit excess and rule-based alerts**. It does not estimate claims, losses, PD, LGD or expected loss.
- Hypothetical aging shifts are not legal changes to invoice due dates; reduced limits are not changes to live insurance coverage.
- Credit-limit values and suspension statuses are not stored as historical events in the current version.

### Technology

`Python` · `SQLite` · `SQL` · `HTML / CSS / JavaScript` · `unittest` · `GitHub Actions` · `Power BI-ready CSVs` · `DAX examples`

**License:** [MIT License](LICENSE) — Copyright (c) 2026 Khaoula Nassiri.
