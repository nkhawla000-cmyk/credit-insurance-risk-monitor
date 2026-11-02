"""Export a self-contained Power BI-ready, reproducible analytics dataset.
All amounts are synthetic MAD.  Sources: validated point-in-time snapshots.
No external Python dependencies, and no real customers are involved.
"""
from __future__ import annotations
import csv
import json
from pathlib import Path
from src.alerts import build_alerts
from src.stress import scenario_grid, AGING_DAYS, LIMIT_CUTS

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / 'outputs'
OUT = ROOT / 'powerbi' / 'datasets'


def _read(name: str) -> list[dict]:
    with (SNAPSHOT / name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def _write(name: str, rows: list[dict], fields: list[str], out: Path):
    out.mkdir(parents=True, exist_ok=True)
    with (out / name).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def export(out: Path = OUT) -> dict:
    kpis = json.loads((SNAPSHOT / 'kpis.json').read_text(encoding='utf8'))
    limits, invoices = _read('credit_limits_snapshot.csv'), _read('invoices_snapshot.csv')
    if len(limits) != int(kpis['credit_limits']) or len(invoices) != int(kpis['invoices_issued']):
        raise ValueError('Snapshot row counts do not match KPI counts; rerun run.py')
    if len({r['limit_id'] for r in limits}) != len(limits):
        raise ValueError('limit_id is not unique')
    if len({r['invoice_id'] for r in invoices}) != len(invoices):
        raise ValueError('invoice_id is not unique')
    limit_ids = {r['limit_id'] for r in limits}
    if any(r['limit_id'] not in limit_ids for r in invoices):
        raise ValueError('Invoice references an unknown credit limit')
    def sumcol(rows, col): return sum(int(r[col]) for r in rows)
    if sumcol(limits,'outstanding_mad') != kpis['outstanding_mad'] or sumcol(invoices,'outstanding_mad') != kpis['outstanding_mad']:
        raise ValueError('Exposure reconciliation failure')
    if sumcol(limits,'over_limit_mad') != kpis['over_limit_mad']:
        raise ValueError('Over-limit reconciliation failure')

    flat = [{**row, 'as_of':kpis['as_of'], 'currency':'MAD'} for row in limits]
    _write('portfolio_flat.csv', flat,
           ['as_of','currency','limit_id','policyholder_id','buyer_id','sector','region',
            'risk_band','status','credit_limit_mad','outstanding_mad','overdue_mad',
            'overdue_30_plus_mad','over_limit_mad','utilization_pct'], out)
    _write('dim_limits.csv', limits,
           ['limit_id','policyholder_id','buyer_id','sector','region','risk_band','status','credit_limit_mad'],out)
    _write('fact_exposure.csv',
           [{'limit_id':r['limit_id'], 'as_of':kpis['as_of'],
            'outstanding_mad':r['outstanding_mad'],'overdue_mad':r['overdue_mad'],
            'overdue_30_plus_mad':r['overdue_30_plus_mad'],'over_limit_mad':r['over_limit_mad']}
            for r in limits],
           ['limit_id','as_of','outstanding_mad','overdue_mad','overdue_30_plus_mad','over_limit_mad'],out)
    _write('fact_invoices.csv',invoices,
           ['invoice_id','limit_id','issue_date','due_date','amount_mad',
            'paid_as_of_mad','outstanding_mad','overdue_mad','days_overdue','aging_bucket'],out)
    alerts = build_alerts(limits, invoices)
    alertrows = [
        {'limit_id':a['limit_id'],'buyer_id':a['buyer_id'],
         'priority':a['priority'],'score':a['score'],
         'outstanding_mad':a['outstanding_mad'],
         'over_limit_mad':a['over_limit_mad'],
         'overdue_30_plus_mad':a['overdue_30_plus_mad'],
         'signals':' | '.join(r['label'] for r in a['reasons'])}
         for a in alerts]
    _write('fact_alerts.csv',alertrows,
           ['limit_id','buyer_id','priority','score','outstanding_mad',
            'over_limit_mad','overdue_30_plus_mad','signals'],out)
    grid = scenario_grid(limits,invoices,kpis['as_of'])
    summaries = []
    scenarios = []
    for days in AGING_DAYS:
        for cut in LIMIT_CUTS:
            scenario = grid[f'{days}_{cut}']
            key = f'D{days:02d}_C{cut:02d}'
            summaries.append({'scenario_key':key,'aging_days':days,'limit_cut_pct':cut,
                 'outstanding_mad':scenario['summary']['outstanding_mad'],
                 'overdue_30_plus_mad':scenario['summary']['overdue_30_plus_mad'],
                 'over_limit_mad':scenario['summary']['over_limit_mad'],
                 'approved_limits_mad':scenario['summary']['approved_limits_mad'],
                 'utilization_pct':scenario['summary']['utilization_pct'],
                 'critical_alerts':scenario['summary']['critical_alerts']})
            scenarios.extend([{'scenario_key':key, **r} for r in scenario['rows']])
    _write('scenario_summary.csv', summaries,
           ['scenario_key','aging_days','limit_cut_pct','outstanding_mad',
            'overdue_30_plus_mad','over_limit_mad','approved_limits_mad',
            'utilization_pct','critical_alerts'],out)
    _write('fact_scenarios.csv',scenarios,
           ['scenario_key','limit_id','buyer_id','policyholder_id','sector','region','status',
            'outstanding_mad','base_limit_mad','scenario_limit_mad',
            'base_overdue_30_mad','scenario_overdue_30_mad','base_over_limit_mad',
            'scenario_over_limit_mad','scenario_aged_90_mad','priority','score'],out)
    report={'as_of':kpis['as_of'],'currency':'MAD','dim_limits':len(limits),
            'fact_exposure':len(limits),'fact_invoices':len(invoices),
            'fact_alerts':len(alertrows),'scenario_summary':len(summaries),
            'fact_scenarios':len(scenarios), 'reconciled_outstanding_mad':kpis['outstanding_mad'],
            'reconciled_over_limit_mad':kpis['over_limit_mad'],
            'all_data_synthetic':True}
    (out/'EXPORT_MANIFEST.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    return report
