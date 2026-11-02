"""Reproducible point-in-time ledger balances, aging buckets and per-limit exposures."""
from __future__ import annotations
import sqlite3
from datetime import date


def age_bucket(days_overdue: int) -> str:
    if days_overdue <= 0:
        return 'not_due'
    if days_overdue <= 30:
        return '1-30'
    if days_overdue <= 60:
        return '31-60'
    if days_overdue <= 90:
        return '61-90'
    return '90+'


def snapshot(conn: sqlite3.Connection, as_of: date) -> dict:
    """Use only issued invoices and payments *dated* on or before as_of."""
    day = as_of.isoformat()
    base = conn.execute('''
        SELECT i.invoice_id,i.limit_id,i.issue_date,i.due_date,i.amount_mad,
               COALESCE(SUM(p.amount_mad),0) as paid_as_of,
               l.policyholder_id,l.buyer_id,l.credit_limit_mad,l.status,
               b.region,b.risk_band,h.sector
        FROM invoices i
        JOIN credit_limits l ON i.limit_id=l.limit_id
        JOIN buyers b ON l.buyer_id=b.buyer_id
        JOIN policyholders h ON l.policyholder_id=h.policyholder_id
        LEFT JOIN payments p ON p.invoice_id=i.invoice_id AND p.payment_date<=?
        WHERE i.issue_date<=?
        GROUP BY i.invoice_id
        ORDER BY i.invoice_id''', (day, day)).fetchall()
    invoices = []
    for (invoice_id, limit_id, issue, due, amount, paid, holder, buyer, limit_amount,
         status, region, risk, sector) in base:
        outstanding = int(amount - paid)
        days = max(0, (as_of-date.fromisoformat(due)).days) if outstanding else 0
        late = outstanding if days else 0
        invoices.append(dict(invoice_id=invoice_id,limit_id=limit_id,
                             policyholder_id=holder,buyer_id=buyer, region=region, sector=sector,
                             risk_band=risk, status=status, issue_date=issue,due_date=due,
                             amount_mad=amount,paid_as_of_mad=paid,outstanding_mad=outstanding,
                             overdue_mad=late,days_overdue=days,aging_bucket=age_bucket(days)))

    credit_limits = conn.execute('''SELECT l.limit_id,l.policyholder_id,l.buyer_id,l.credit_limit_mad,
                                 l.status,b.region,b.risk_band,h.sector
                                 FROM credit_limits l
                                 JOIN buyers b ON l.buyer_id=b.buyer_id
                                 JOIN policyholders h ON l.policyholder_id=h.policyholder_id
                                 ORDER BY l.limit_id''').fetchall()
    per_limit = {}
    for limit_id, holder, buyer, credit_limit, status, region, risk, sector in credit_limits:
        per_limit[limit_id] = dict(limit_id=limit_id,policyholder_id=holder,
                                   buyer_id=buyer,sector=sector,region=region,
                                   risk_band=risk,status=status,credit_limit_mad=credit_limit,
                                   outstanding_mad=0,overdue_mad=0,overdue_30_plus_mad=0,
                                   over_limit_mad=0,utilization_pct=0.0)
    for inv in invoices:
        p = per_limit[inv['limit_id']]
        p['outstanding_mad'] += inv['outstanding_mad']
        p['overdue_mad'] += inv['overdue_mad']
        if inv['days_overdue']>30:
            p['overdue_30_plus_mad'] += inv['outstanding_mad']
    for p in per_limit.values():
        p['over_limit_mad'] = max(0, p['outstanding_mad'] - p['credit_limit_mad'])
        p['utilization_pct'] = round(100*p['outstanding_mad']/p['credit_limit_mad'],2)
    total_outstanding = sum(x['outstanding_mad'] for x in invoices)
    total_overdue = sum(x['overdue_mad'] for x in invoices)
    exposure_by_buyer = {}
    for p in per_limit.values():
        exposure_by_buyer[p['buyer_id']] = exposure_by_buyer.get(p['buyer_id'],0)+p['outstanding_mad']
    top_ten = sum(sorted(exposure_by_buyer.values(),reverse=True)[:10])
    kpis = dict(as_of=day,currency='MAD',policyholders=conn.execute('SELECT COUNT(*) FROM policyholders').fetchone()[0],
                buyers=conn.execute('SELECT COUNT(*) FROM buyers').fetchone()[0],
                credit_limits=len(per_limit),invoices_issued=len(invoices),
                outstanding_mad=total_outstanding,overdue_mad=total_overdue,
                overdue_30_plus_mad=sum(p['overdue_30_plus_mad'] for p in per_limit.values()),
                approved_limits_mad=sum(p['credit_limit_mad'] for p in per_limit.values()),
                over_limit_mad=sum(p['over_limit_mad'] for p in per_limit.values()),
                overdue_share_pct=round(100*total_overdue/total_outstanding,2) if total_outstanding else 0,
                global_utilization_pct=round(100*total_outstanding/sum(p['credit_limit_mad'] for p in per_limit.values()),2) if per_limit else 0,
                top_10_buyers_exposure_pct=round(100*top_ten/total_outstanding,2) if total_outstanding else 0,
                rejected_rows=conn.execute('SELECT COUNT(*) FROM rejected_rows').fetchone()[0])
    return {'kpis':kpis,'invoices':invoices,'credit_limits':list(per_limit.values())}
