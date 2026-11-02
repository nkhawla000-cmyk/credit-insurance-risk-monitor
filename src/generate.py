"""Reproducible fictional B2B trade-credit insurance sample (no real client records)."""
from __future__ import annotations
import csv
import random
from datetime import date, timedelta
from pathlib import Path

SECTORS = ('Automobile', 'Agroalimentaire', 'Textile', 'Construction', 'Commerce', 'Services')
REGIONS = ('Casablanca-Settat', 'Rabat-Sale-Kenitra', 'Tanger-Tetouan-Al Hoceima',
           'Fes-Meknes', 'Marrakech-Safi', 'Souss-Massa')


def write_csv(path: Path, headers: list[str], rows: list[list]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


def generate(folder: Path, seed: int = 2026) -> dict[str, int]:
    """Generate a reproducible 5-table dataset including deliberate invalid rows."""
    folder = Path(folder)
    rng = random.Random(seed)
    holders = [[f'H{x:03}', f'Entreprise assuree fictive {x:02}', rng.choice(SECTORS)]
               for x in range(1, 9)]
    buyers = [[f'B{x:03}', f'Acheteur fictif {x:03}', rng.choice(REGIONS),
               rng.choices(['low', 'medium', 'high'], weights=[5, 3, 2])[0]]
              for x in range(1, 81)]
    write_csv(folder/'policyholders.csv', ['policyholder_id', 'policyholder_name', 'sector'], holders)
    write_csv(folder/'buyers.csv', ['buyer_id', 'buyer_name', 'region', 'risk_band'], buyers)

    possible_pairs = [(h[0], b[0]) for h in holders for b in buyers]
    pairs = rng.sample(possible_pairs, 140)
    buyer_lookup = {b[0]: b for b in buyers}
    limits = []
    for n, (holder_id, buyer_id) in enumerate(pairs, start=1):
        status = rng.choices(['active', 'suspended'], weights=[93, 7])[0]
        limits.append([f'L{n:04}', holder_id, buyer_id,
                       rng.choice([80000, 120000, 200000, 320000, 500000, 750000]), status])
    write_csv(folder/'credit_limits.csv',
              ['limit_id', 'policyholder_id', 'buyer_id', 'credit_limit_mad', 'status'], limits)

    invoices = []
    payments = []
    payment_no = 1
    invoice_no = 1
    for limit_id, _, buyer_id, _, _ in limits:
        for _ in range(6):
            issue = date(2026, 1, 1) + timedelta(days=rng.randint(0, 275))
            due = issue + timedelta(days=rng.choice([30, 45, 60, 90]))
            amount = rng.randrange(5000, 85001, 500)
            iid = f'I{invoice_no:05}'
            invoices.append([iid, limit_id, issue.isoformat(), due.isoformat(), amount])
            invoice_no += 1
            risk = buyer_lookup[buyer_id][3]
            if risk == 'low':
                fraction = rng.choices([0, 0.5, 1], weights=[15, 25, 60])[0]
            elif risk == 'medium':
                fraction = rng.choices([0, 0.5, 1], weights=[35, 35, 30])[0]
            else:
                fraction = rng.choices([0, 0.5, 1], weights=[55, 30, 15])[0]
            paid = int(amount * fraction)
            if paid:
                first = paid if paid < 2 else paid // 2
                steps = [first] if first == paid else [first, paid - first]
                for j, v in enumerate(steps):
                    day = due + timedelta(days=rng.choice([-15, 0, 10, 30, 60, 95]) + j * 8)
                    day = max(day, issue)
                    payments.append([f'PM{payment_no:06}', iid, day.isoformat(), v])
                    payment_no += 1

    # Quarantine cases (never treated as valid business records):
    invoices.append(invoices[0][:])  # duplicate ID
    invoices.append(['I_BAD_REF', 'L9999', '2026-04-05', '2026-05-05', 10000])
    payments.append(['PM_BAD_DATE', 'I00001', '2025-01-01', 100])
    payments.append(['PM_BAD_OVERPAY', 'I00001', '2026-08-01', invoices[0][4] + 10000])
    write_csv(folder/'invoices.csv',
              ['invoice_id', 'limit_id', 'issue_date', 'due_date', 'amount_mad'], invoices)
    write_csv(folder/'payments.csv',
              ['payment_id', 'invoice_id', 'payment_date', 'amount_mad'], payments)
    return {'policyholders': len(holders), 'buyers': len(buyers), 'credit_limits': len(limits),
            'valid_invoices': invoice_no-1, 'payments_including_issues': len(payments)}


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    print(generate(root/'data'))
