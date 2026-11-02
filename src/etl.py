"""Import and quality-control fictional trade-credit data into SQLite.

Amount fields are whole MAD (INTEGER) to avoid floating point currency errors.
"""
from __future__ import annotations
import csv
import sqlite3
from datetime import date
from pathlib import Path

INPUT_COLUMNS = {
    'policyholders': ['policyholder_id', 'policyholder_name', 'sector'],
    'buyers': ['buyer_id', 'buyer_name', 'region', 'risk_band'],
    'credit_limits': ['limit_id', 'policyholder_id', 'buyer_id', 'credit_limit_mad', 'status'],
    'invoices': ['invoice_id', 'limit_id', 'issue_date', 'due_date', 'amount_mad'],
    'payments': ['payment_id', 'invoice_id', 'payment_date', 'amount_mad'],
}


def schema(conn: sqlite3.Connection):
    conn.execute('PRAGMA foreign_keys = ON')
    conn.executescript('''
    CREATE TABLE IF NOT EXISTS policyholders (
      policyholder_id TEXT PRIMARY KEY, policyholder_name TEXT NOT NULL, sector TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS buyers (
      buyer_id TEXT PRIMARY KEY, buyer_name TEXT NOT NULL, region TEXT NOT NULL,
      risk_band TEXT NOT NULL CHECK(risk_band IN ('low','medium','high')));
    CREATE TABLE IF NOT EXISTS credit_limits (
      limit_id TEXT PRIMARY KEY,
      policyholder_id TEXT NOT NULL REFERENCES policyholders(policyholder_id),
      buyer_id TEXT NOT NULL REFERENCES buyers(buyer_id),
      credit_limit_mad INTEGER NOT NULL CHECK(credit_limit_mad > 0),
      status TEXT NOT NULL CHECK(status IN ('active','suspended')),
      UNIQUE(policyholder_id, buyer_id));
    CREATE TABLE IF NOT EXISTS invoices (
      invoice_id TEXT PRIMARY KEY,
      limit_id TEXT NOT NULL REFERENCES credit_limits(limit_id),
      issue_date TEXT NOT NULL, due_date TEXT NOT NULL,
      amount_mad INTEGER NOT NULL CHECK(amount_mad > 0));
    CREATE TABLE IF NOT EXISTS payments (
      payment_id TEXT PRIMARY KEY,
      invoice_id TEXT NOT NULL REFERENCES invoices(invoice_id),
      payment_date TEXT NOT NULL, amount_mad INTEGER NOT NULL CHECK(amount_mad > 0));
    CREATE TABLE IF NOT EXISTS rejected_rows (
      anomaly_id INTEGER PRIMARY KEY AUTOINCREMENT,
      source_file TEXT NOT NULL, csv_row INTEGER NOT NULL,
      reason TEXT NOT NULL);
    CREATE INDEX IF NOT EXISTS idx_invoices_limit ON invoices(limit_id);
    CREATE INDEX IF NOT EXISTS idx_payments_invoice_date ON payments(invoice_id,payment_date);
    ''')


def _int(value: str, label: str) -> int:
    try:
        v = int(value)
    except (ValueError, TypeError) as exc:
        raise ValueError(f'{label} must be an integer MAD amount') from exc
    if v <= 0:
        raise ValueError(f'{label} must be positive')
    return v


def _iso(value: str, label: str) -> str:
    try:
        return date.fromisoformat(value).isoformat()
    except (ValueError, TypeError) as exc:
        raise ValueError(f'invalid {label}') from exc


def _required(row: dict, field: str) -> str:
    result = (row.get(field) or '').strip()
    if not result:
        raise ValueError(f'missing {field}')
    return result


def _exists(conn, table, col, value):
    # All identifiers here are fixed in source; never use untrusted SQL identifiers.
    return conn.execute(f'SELECT 1 FROM {table} WHERE {col}=?', (value,)).fetchone() is not None


def _parse(conn: sqlite3.Connection, table: str, row: dict) -> tuple:
    if table == 'policyholders':
        return tuple(_required(row, c) for c in INPUT_COLUMNS[table])
    if table == 'buyers':
        values = tuple(_required(row, c) for c in INPUT_COLUMNS[table])
        if values[3] not in {'low', 'medium', 'high'}:
            raise ValueError('risk_band outside allowed labels')
        return values
    if table == 'credit_limits':
        ident, holder, buyer = [_required(row, c) for c in INPUT_COLUMNS[table][:3]]
        lim = _int(_required(row, 'credit_limit_mad'), 'credit_limit_mad')
        status = _required(row, 'status')
        if status not in {'active', 'suspended'}:
            raise ValueError('invalid status')
        if not _exists(conn, 'policyholders', 'policyholder_id', holder):
            raise ValueError('unknown policyholder_id')
        if not _exists(conn, 'buyers', 'buyer_id', buyer):
            raise ValueError('unknown buyer_id')
        return ident, holder, buyer, lim, status
    if table == 'invoices':
        ident, limit_id = _required(row, 'invoice_id'), _required(row, 'limit_id')
        issue = _iso(_required(row, 'issue_date'), 'issue_date')
        due = _iso(_required(row, 'due_date'), 'due_date')
        if due < issue:
            raise ValueError('due_date precedes issue_date')
        if not _exists(conn, 'credit_limits', 'limit_id', limit_id):
            raise ValueError('unknown limit_id')
        return ident, limit_id, issue, due, _int(_required(row, 'amount_mad'), 'amount_mad')
    if table == 'payments':
        payment_id, invoice_id = _required(row, 'payment_id'), _required(row, 'invoice_id')
        paid_on = _iso(_required(row, 'payment_date'), 'payment_date')
        amount = _int(_required(row, 'amount_mad'), 'amount_mad')
        invoice = conn.execute('SELECT issue_date,amount_mad FROM invoices WHERE invoice_id=?',
                               (invoice_id,)).fetchone()
        if not invoice:
            raise ValueError('unknown invoice_id')
        if paid_on < invoice[0]:
            raise ValueError('payment_date precedes invoice issue_date')
        total = conn.execute('SELECT COALESCE(SUM(amount_mad),0) FROM payments WHERE invoice_id=?',
                             (invoice_id,)).fetchone()[0]
        if total + amount > invoice[1]:
            raise ValueError('cumulative payments exceed invoice amount')
        return payment_id, invoice_id, paid_on, amount
    raise ValueError(f'unsupported table: {table}')


def import_dataset(conn: sqlite3.Connection, folder: Path) -> dict[str, int]:
    """Atomic reload: no duplication on repeated runs, rejected rows preserved in audit table."""
    schema(conn)
    folder = Path(folder)
    accepted: dict[str, int] = {}
    tables = list(INPUT_COLUMNS)
    try:
        conn.execute('BEGIN')
        for table in list(reversed(tables)) + ['rejected_rows']:
            conn.execute(f'DELETE FROM {table}')
        for table, columns in INPUT_COLUMNS.items():
            with (folder/f'{table}.csv').open('r', encoding='utf-8-sig', newline='') as f:
                reader = csv.DictReader(f)
                if not set(columns).issubset(reader.fieldnames or []):
                    raise ValueError(f'{table}.csv missing required columns: {columns}')
                seen: set[str] = set()
                accepted[table] = 0
                for row_no, row in enumerate(reader, start=2):
                    try:
                        identity = _required(row, columns[0])
                        if identity in seen:
                            raise ValueError('duplicate ID in source CSV')
                        seen.add(identity)
                        values = _parse(conn, table, row)
                        placeholders = ','.join(['?']*len(columns))
                        conn.execute(f'INSERT INTO {table} VALUES({placeholders})', values)
                        accepted[table] += 1
                    except (ValueError, sqlite3.IntegrityError) as exc:
                        conn.execute('''INSERT INTO rejected_rows(source_file,csv_row,reason)
                                        VALUES(?,?,?)''', (f'{table}.csv', row_no, str(exc)))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    accepted['rejected_rows'] = conn.execute('SELECT COUNT(*) FROM rejected_rows').fetchone()[0]
    return accepted
