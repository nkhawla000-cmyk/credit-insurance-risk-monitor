import csv
import sqlite3
import tempfile
import unittest
from datetime import date
from pathlib import Path
from src.generate import generate, write_csv
from src.etl import import_dataset, schema
from src.metrics import age_bucket, snapshot


class TestStage1(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        generate(self.root, seed=1)
        self.conn=sqlite3.connect(':memory:')
        self.counts=import_dataset(self.conn,self.root)
    def tearDown(self):
        self.conn.close();self.tmp.cleanup()
    def test_expected_invalid_records_quarantined(self):
        self.assertEqual(self.counts['rejected_rows'],4)
    def test_840_valid_invoices(self):
        self.assertEqual(self.counts['invoices'],840)
    def test_reimport_is_idempotent(self):
        s1=snapshot(self.conn,date(2026,10,31))['kpis']
        import_dataset(self.conn,self.root)
        s2=snapshot(self.conn,date(2026,10,31))['kpis']
        self.assertEqual(s1,s2)
    def test_paid_as_of_never_exceeds_invoice_amount(self):
        for i in snapshot(self.conn,date(2026,12,31))['invoices']:
            self.assertLessEqual(i['paid_as_of_mad'],i['amount_mad'])
    def test_payments_are_temporal_and_snapshot_changes(self):
        before=snapshot(self.conn,date(2026,5,1))['kpis']
        later=snapshot(self.conn,date(2026,10,31))['kpis']
        self.assertNotEqual(before['invoices_issued'],later['invoices_issued'])
        self.assertLessEqual(before['invoices_issued'],later['invoices_issued'])
    def test_payments_in_future_not_used(self):
        self.conn.execute("INSERT INTO payments VALUES ('FUTURE','I00001','2027-01-01',1)")
        before=snapshot(self.conn,date(2026,10,31))['invoices'][0]['paid_as_of_mad']
        self.conn.execute("DELETE FROM payments WHERE payment_id='FUTURE'")
        after=snapshot(self.conn,date(2026,10,31))['invoices'][0]['paid_as_of_mad']
        self.assertEqual(before,after)
    def test_total_equals_sum_of_exposures(self):
        d=snapshot(self.conn,date(2026,10,31))
        self.assertEqual(d['kpis']['outstanding_mad'],sum(p['outstanding_mad'] for p in d['credit_limits']))
    def test_limit_overages_are_nonnegative(self):
        d=snapshot(self.conn,date(2026,10,31))
        for p in d['credit_limits']:
            self.assertEqual(p['over_limit_mad'],max(0,p['outstanding_mad']-p['credit_limit_mad']))
    def test_overdue_30_plus_subset_of_overdue(self):
        d=snapshot(self.conn,date(2026,10,31))['kpis']
        self.assertLessEqual(d['overdue_30_plus_mad'],d['overdue_mad'])
    def test_aging_bucket_boundaries(self):
        for days,expected in [(0,'not_due'),(1,'1-30'),(30,'1-30'),(31,'31-60'),(60,'31-60'),(61,'61-90'),(90,'61-90'),(91,'90+')]:
            self.assertEqual(age_bucket(days),expected)
    def test_foreign_keys_enabled(self):
        self.assertEqual(self.conn.execute('PRAGMA foreign_keys').fetchone()[0],1)
    def test_unknown_invoice_payment_rejected(self):
        with (self.root/'payments.csv').open('a',encoding='utf-8') as f:
            f.write('PM_BAD_ORPHAN,UNKNOWN,2026-05-01,100\n')
        c=import_dataset(self.conn,self.root)
        self.assertEqual(c['rejected_rows'],5)
    def test_duplicate_covered_pair_rejected(self):
        with (self.root/'credit_limits.csv').open('r',encoding='utf-8') as f:
            rows=list(csv.DictReader(f))
        row=rows[0].copy();row['limit_id']='L9999'
        with (self.root/'credit_limits.csv').open('a',encoding='utf-8',newline='') as f:
            csv.writer(f).writerow(row.values())
        c=import_dataset(self.conn,self.root)
        self.assertEqual(c['rejected_rows'],5)


if __name__=='__main__': unittest.main()
