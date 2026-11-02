"""Build a self-contained, offline, interactive portfolio dashboard.

Usage:
    python3 run.py --as-of 2026-10-31
    python3 build_dashboard.py
    open dashboard/index.html   # macOS, or double-click the file

No external Python or JavaScript dependencies are required.
"""
from __future__ import annotations
import csv
import json
from pathlib import Path
from src.alerts import build_alerts
from src.stress import scenario_grid

ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / 'outputs'
DASHBOARD = ROOT / 'dashboard'


def read_csv(file_name: str) -> list[dict]:
    path = OUTPUTS / file_name
    if not path.is_file():
        raise FileNotFoundError(f"Missing {path}. Run: python3 run.py --as-of 2026-10-31")
    with path.open(encoding='utf-8-sig', newline='') as file:
        return list(csv.DictReader(file))


def prepare_payload() -> dict:
    kpis_path = OUTPUTS / 'kpis.json'
    if not kpis_path.is_file():
        raise FileNotFoundError(f"Missing {kpis_path}. Run the pipeline first.")
    kpis = json.loads(kpis_path.read_text(encoding='utf-8'))
    limits = read_csv('credit_limits_snapshot.csv')
    invoices = read_csv('invoices_snapshot.csv')
    # Avoid silent inconsistencies when input files come from different runs.
    if len(limits) != kpis['credit_limits'] or len(invoices) != kpis['invoices_issued']:
        raise ValueError('Snapshot row counts do not match kpis.json. Rerun python3 run.py.')
    if sum(int(row['outstanding_mad']) for row in limits) != kpis['outstanding_mad']:
        raise ValueError('Snapshot outstanding differs from kpis.json. Rerun python3 run.py.')
    if sum(int(row['outstanding_mad']) for row in invoices) != kpis['outstanding_mad']:
        raise ValueError('Invoice totals differ from kpis.json. Rerun python3 run.py.')

    cols_limit = ['limit_id', 'policyholder_id', 'buyer_id', 'sector', 'region',
                  'risk_band', 'status']
    cols_invoice = ['invoice_id', 'limit_id', 'buyer_id', 'aging_bucket']
    num_limit = ['credit_limit_mad', 'outstanding_mad', 'overdue_mad',
                 'overdue_30_plus_mad', 'over_limit_mad']
    num_invoice = ['outstanding_mad', 'overdue_mad', 'days_overdue']
    out_limits = [{**{k: row[k] for k in cols_limit},
                   **{k: int(row[k]) for k in num_limit}} for row in limits]
    out_invoices = [{**{k: row[k] for k in cols_invoice},
                    **{k: int(row[k]) for k in num_invoice}} for row in invoices]
    return {'meta': {'as_of': kpis['as_of'], 'currency': kpis['currency'],
                     'rejected_rows': kpis['rejected_rows'],
                     'policyholders': kpis['policyholders']},
            'limits': out_limits, 'invoices': out_invoices,
            'alerts': build_alerts(out_limits, out_invoices),
            'stress': scenario_grid(out_limits, invoices, kpis['as_of'])}


def main() -> Path:
    payload = prepare_payload()
    template = (DASHBOARD / 'template.html').read_text(encoding='utf-8')
    marker = '/*__PORTFOLIO_DATA__*/'
    if template.count(marker) != 1:
        raise ValueError('Dashboard template must contain exactly one data marker')
    serialized = json.dumps(payload, ensure_ascii=False, separators=(',', ':'))
    # Avoid accidentally closing the script tag with third-party data.
    serialized = serialized.replace('<', r'\u003c').replace('>', r'\u003e')
    html = template.replace(marker, 'const DATA = ' + serialized + ';')
    DASHBOARD.mkdir(parents=True, exist_ok=True)
    path = DASHBOARD / 'index.html'
    path.write_text(html, encoding='utf-8')
    print(f'Dashboard generated: {path}')
    print(f"Snapshot: {payload['meta']['as_of']} | {len(payload['limits'])} limits | {len(payload['invoices'])} invoices")
    return path


if __name__ == '__main__':
    main()
