"""Heuristic, fully explainable monitoring alerts for synthetic trade-credit data.

A priority index is NOT a probability of default or an insurance coverage decision.
Rules use only a point-in-time snapshot, without leaking future payments.
"""
from __future__ import annotations
from collections import defaultdict


def build_alerts(limits: list[dict], invoices: list[dict]) -> list[dict]:
    by_limit: dict[str, dict] = defaultdict(lambda: {'ninety_plus': 0, 'invoice_count': 0})
    for invoice in invoices:
        record = by_limit[invoice['limit_id']]
        record['invoice_count'] += 1
        if invoice['aging_bucket'] == '90+':
            record['ninety_plus'] += int(invoice['outstanding_mad'])

    alerts = []
    for line in limits:
        outstanding = int(line['outstanding_mad'])
        if outstanding <= 0:
            continue
        limit = int(line['credit_limit_mad'])
        excess = max(0, outstanding - limit)
        late30 = int(line['overdue_30_plus_mad'])
        ninety = by_limit[line['limit_id']]['ninety_plus']
        reasons = []

        def add(code: str, label: str, points: int, detail: str):
            reasons.append({'code': code, 'label': label, 'points': points, 'detail': detail})

        if excess > 0:
            add('over_limit', 'Limite dépassée', 4,
                f'Encours supérieur à la limite de {excess:,} MAD.'.replace(',', ' '))
        if ninety >= 25_000 and ninety >= 0.25 * outstanding:
            add('aged_90', 'Créances > 90 jours', 3,
                f'{ninety:,} MAD échus depuis plus de 90 jours.'.replace(',', ' '))
        if late30 >= 50_000 and late30 >= 0.40 * outstanding:
            add('late_30', 'Retards > 30 jours', 2,
                f'{late30:,} MAD échus depuis plus de 30 jours.'.replace(',', ' '))
        if line['status'] == 'suspended':
            add('suspended', 'Limite suspendue', 2,
                'Limite au statut suspendu avec encours restant dû.')
        # A simulated pre-assigned risk band cannot, on its own, create an alert.
        if reasons and line['risk_band'] == 'high':
            add('risk_profile', 'Profil simulé élevé', 1,
                'Classification de risque synthétique, non validée comme score de crédit.')
        score = sum(x['points'] for x in reasons)
        if score < 2:
            continue
        priority = 'critical' if score >= 7 else 'high' if score >= 4 else 'watch'
        alerts.append({
            'limit_id': line['limit_id'], 'buyer_id': line['buyer_id'],
            'policyholder_id': line['policyholder_id'], 'sector': line['sector'],
            'region': line['region'], 'risk_band': line['risk_band'],
            'status': line['status'], 'priority': priority, 'score': score,
            'outstanding_mad': outstanding, 'credit_limit_mad': limit,
            'over_limit_mad': excess, 'overdue_30_plus_mad': late30,
            'overdue_90_plus_mad': ninety, 'reasons': reasons,
        })
    return sorted(alerts, key=lambda x: (-x['score'], -x['outstanding_mad'], x['limit_id']))
