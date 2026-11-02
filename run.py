"""Stage 1 - deterministic ingestion and historical portfolio KPIs."""
from __future__ import annotations
import argparse
import csv
import json
import sqlite3
from datetime import date
from pathlib import Path
from src.generate import generate
from src.etl import import_dataset
from src.metrics import snapshot

ROOT=Path(__file__).resolve().parent


def export(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not data:
        return
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]))
        w.writeheader();w.writerows(data)


def main(as_of: date) -> dict:
    if not (ROOT/'data/buyers.csv').exists():
        generate(ROOT/'data')
    db=ROOT/'outputs/insurance_monitor.sqlite3'
    db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db) as conn:
        counts=import_dataset(conn,ROOT/'data')
        result=snapshot(conn,as_of)
        anomaly=[dict(source_file=x[0],csv_row=x[1],reason=x[2]) for x in
                 conn.execute('SELECT source_file,csv_row,reason FROM rejected_rows ORDER BY anomaly_id')]
    export(ROOT/'outputs/invoices_snapshot.csv',result['invoices'])
    export(ROOT/'outputs/credit_limits_snapshot.csv',result['credit_limits'])
    export(ROOT/'outputs/anomalies.csv',anomaly)
    (ROOT/'outputs/kpis.json').write_text(json.dumps(result['kpis'],indent=2,ensure_ascii=False),encoding='utf-8')
    (ROOT/'outputs/quality_summary.json').write_text(json.dumps(counts,indent=2),encoding='utf-8')
    return result['kpis']


if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Educational trade credit insurance portfolio monitor, stage 1')
    parser.add_argument('--as-of',default='2026-10-31',help='YYYY-MM-DD; historical snapshot cutoff')
    args=parser.parse_args()
    print(json.dumps(main(date.fromisoformat(args.as_of)),indent=2,ensure_ascii=False))
