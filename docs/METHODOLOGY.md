# Methodology, assumptions and limitations

## 1. Purpose and data provenance

This is a **self-contained educational demonstrator of trade credit insurance portfolio monitoring**. All records are synthetic. The dataset represents insured sellers, their buyer/debtors, buyer-specific credit-limit relationships, invoices and dated cash receipts. No real claims or underwriting history is included.

The snapshot date used in the public demo is **31 October 2026**. The scenarios are deliberately stressed to make decision-support signals visible. **Neither buyer risk bands nor simulated overdue proportions are estimates of the Moroccan market.**

## 2. As-of receivables and quality controls

For each invoice, remaining exposure at the selected date is the issued amount minus payments dated on or before that date, floored at zero. Receipts recorded after the selected date are not used. The pipeline rejects invalid records, maintains relational integrity in SQLite and exports reconciled invoice and credit-limit snapshots.

Portfolio aggregates are calculated from **limit-level exposures** rather than summing the same exposure once per invoice. Values are reported in MAD. Dashboard views respect user filters. See tests in `tests/` for temporal and reconciliation checks.

## 3. Explainable early warnings

A limit relationship can trigger the following transparent, *non-predictive* rules:

| Signal | Points | Requirement |
|---|---:|---|
| Credit limit exceeded | +4 | Remaining exposure exceeds the simulated limit |
| Invoices more than 90 days overdue | +3 | At least MAD 25,000 and 25% of exposure |
| Invoices more than 30 days overdue | +2 | At least MAD 50,000 and 40% of exposure |
| Suspended limit with positive exposure | +2 | Simulated suspension status and nonzero exposure |
| Synthetic high-risk band | +1 | Counts only when another signal exists |

Priority categories: **critical** (score >= 7), **high** (4–6), **watch** (2–3). These are triage flags, **not** validated credit scores, probabilities of default or indemnification decisions.

In the deliberately degraded example, **119 of 140 limit relationships** receive at least one warning and **about 80%** of the receivables are overdue. These levels are *design choices for demonstration*, not an observed industry benchmark. For a general-purpose operational system, thresholds and data generation would require validation against historical outcomes.

## 4. Scenario-based sensitivity analysis

The module evaluates **30 scenarios**: five hypothetical aging shifts (0, 15, 30, 45, 60 days) crossed with six simulated limit reductions (0%, 10%, 20%, 30%, 40%, 50%).

- Invoice amounts, historic payments and total outstanding exposure do **not** change.
- The aging shift models a counterfactual deterioration of unpaid invoice aging; it is not a contractual change to due dates or a forecast.
- The limit shock reduces simulated credit-limit amounts for analytical comparison; it does not amend live insurance policies.
- For each limit relationship, excess is `max(outstanding - scenario_limit, 0)`.
- The same explainable warning rules are recomputed under each scenario.

This is **sensitivity analysis**, not a calibrated economic stress test and **not** a calculation of claims, insurer losses, PD, LGD, EAD or expected loss.

## 5. Known limitations and next steps

- The dataset has no claims, default targets, realized recoveries, premiums or policy-level underwriting outcomes.
- No statistical validation, predictive model, fairness review, or backtesting against external real-world records is claimed.
- The credit-limit and suspension history is represented as snapshot information, not a complete event log.
- Sensitivity results should be interpreted as decision-support demonstrations for human review rather than automatic decisions.
- Future extensions could model versioned credit limits, recoveries and claims using **suitably sourced and permitted** datasets, then evaluate calibration or predictive accuracy if targets exist.

## 6. Reproduction and validation

Run `python3 -m src.generate`, `python3 run.py --as-of 2026-10-31`, `python3 export_powerbi.py`, `python3 build_dashboard.py` and `python3 -m unittest discover -s tests -v` from the project root. The verified release passes **41 automated tests**.
