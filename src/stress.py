"""Transparent, static what-if stress simulations on synthetic credit-insurance snapshots.

No prediction, cash-flow forecast, coverage determination or payment history mutation.
Two independent counterfactual shocks:
  * aging_days: move unpaid invoice due dates earlier by this many days while
    keeping the snapshot date and balances fixed;
  * limit_cut_pct: uniformly reduce approved monitoring limits by this percent.
All alerts are recalculated using the exact same rules as the Early Warning Center.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import date
from src.alerts import build_alerts

AGING_DAYS = (0, 15, 30, 45, 60)
LIMIT_CUTS = (0, 10, 20, 30, 40, 50)


def bucket(days_late: int) -> str:
    if days_late <= 0: return 'not_due'
    if days_late <= 30: return '1-30'
    if days_late <= 60: return '31-60'
    if days_late <= 90: return '61-90'
    return '90+'


def simulate(limits: list[dict], invoices: list[dict], as_of: str,
             aging_days: int = 0, limit_cut_pct: int = 0) -> dict:
    if aging_days not in AGING_DAYS or limit_cut_pct not in LIMIT_CUTS:
        raise ValueError('Scenario parameters must match the documented grid')
    snapshot_date = date.fromisoformat(as_of)
    reference = {row['limit_id']: row for row in limits}
    by_limit = defaultdict(lambda: {'outstanding': 0, 'overdue': 0, 'overdue30': 0, 'aged90': 0})
    shocked_invoices = []
    for inv in invoices:
        limit_id = inv['limit_id']
        if limit_id not in reference:
            raise ValueError(f'Unknown limit: {limit_id}')
        unpaid = int(inv['outstanding_mad'])
        days_late = (snapshot_date - date.fromisoformat(inv['due_date'])).days + aging_days
        b = bucket(days_late)
        parts = by_limit[limit_id]
        parts['outstanding'] += unpaid
        if days_late > 0:
            parts['overdue'] += unpaid
        if days_late > 30:
            parts['overdue30'] += unpaid
        if days_late > 90:
            parts['aged90'] += unpaid
        shocked_invoices.append({'invoice_id': inv['invoice_id'], 'limit_id': limit_id,
                                 'aging_bucket': b, 'outstanding_mad': unpaid})
    shocked_limits = []
    for row in limits:
        base = int(row['credit_limit_mad'])
        outstanding = int(row['outstanding_mad'])
        parts = by_limit[row['limit_id']]
        if parts['outstanding'] != outstanding:
            raise ValueError(f"Invoice/limit snapshot mismatch for {row['limit_id']}")
        cut_limit = base * (100 - limit_cut_pct) // 100
        shocked_limits.append({**row, 'credit_limit_mad': cut_limit,
                               'overdue_mad': parts['overdue'],
                               'overdue_30_plus_mad': parts['overdue30'],
                               'over_limit_mad': max(0, outstanding - cut_limit)})
    alerts = build_alerts(shocked_limits, shocked_invoices)
    alert_map = {a['limit_id']: a for a in alerts}
    rows = []
    for base, shocked in zip(limits, shocked_limits):
        aid = base['limit_id']
        a = alert_map.get(aid)
        parts = by_limit[aid]
        rows.append({
            'limit_id': aid, 'buyer_id': base['buyer_id'],
            'policyholder_id': base['policyholder_id'], 'sector': base['sector'],
            'region': base['region'], 'status': base['status'],
            'outstanding_mad': int(base['outstanding_mad']),
            'base_limit_mad': int(base['credit_limit_mad']),
            'scenario_limit_mad': shocked['credit_limit_mad'],
            'base_overdue_30_mad': int(base['overdue_30_plus_mad']),
            'scenario_overdue_30_mad': parts['overdue30'],
            'base_over_limit_mad': int(base['over_limit_mad']),
            'scenario_over_limit_mad': shocked['over_limit_mad'],
            'scenario_aged_90_mad': parts['aged90'],
            'priority': a['priority'] if a else 'none',
            'score': a['score'] if a else 0,
        })
    total_outstanding = sum(r['outstanding_mad'] for r in rows)
    base_limits = sum(r['base_limit_mad'] for r in rows)
    scenario_limits = sum(r['scenario_limit_mad'] for r in rows)
    return {
        'aging_days': aging_days, 'limit_cut_pct': limit_cut_pct,
        'summary': {
            'outstanding_mad': total_outstanding,
            'approved_limits_mad': scenario_limits,
            'base_approved_limits_mad': base_limits,
            'overdue_30_plus_mad': sum(r['scenario_overdue_30_mad'] for r in rows),
            'base_overdue_30_plus_mad': sum(r['base_overdue_30_mad'] for r in rows),
            'over_limit_mad': sum(r['scenario_over_limit_mad'] for r in rows),
            'base_over_limit_mad': sum(r['base_over_limit_mad'] for r in rows),
            'utilization_pct': round(100*total_outstanding/scenario_limits, 2) if scenario_limits else 0,
            'critical_alerts': sum(a['priority']=='critical' for a in alerts),
            'high_alerts': sum(a['priority']=='high' for a in alerts),
            'watch_alerts': sum(a['priority']=='watch' for a in alerts),
        },
        'rows': rows,
    }


def scenario_grid(limits: list[dict], invoices: list[dict], as_of: str) -> dict:
    return {f'{d}_{p}': simulate(limits, invoices, as_of, d, p)
            for d in AGING_DAYS for p in LIMIT_CUTS}
