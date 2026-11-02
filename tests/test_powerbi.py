import csv
import tempfile
import unittest
from pathlib import Path
from src.bi_export import export

class TestBIExport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.manifest = export(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def rows(self, file):
        with (self.root/file).open(encoding='utf-8-sig',newline='') as f:
            return list(csv.DictReader(f))

    def test_snapshot_counts(self):
        self.assertEqual(self.manifest['dim_limits'],140)
        self.assertEqual(self.manifest['fact_invoices'],840)
        self.assertEqual(self.manifest['scenario_summary'],30)
        self.assertEqual(self.manifest['fact_scenarios'],4200)

    def test_one_row_per_limit(self):
        rows=self.rows('dim_limits.csv')
        self.assertEqual(len({x['limit_id'] for x in rows}), len(rows))

    def test_invoices_join(self):
        limits={r['limit_id'] for r in self.rows('dim_limits.csv')}
        self.assertTrue(all(r['limit_id'] in limits for r in self.rows('fact_invoices.csv')))

    def test_flat_reconciles_kpi(self):
        self.assertEqual(sum(int(r['outstanding_mad']) for r in self.rows('portfolio_flat.csv')), 22867875)
        self.assertEqual(sum(int(r['over_limit_mad']) for r in self.rows('portfolio_flat.csv')), 3426375)

    def test_zero_scenario_reconciles(self):
        baseline=next(x for x in self.rows('scenario_summary.csv') if x['scenario_key']=='D00_C00')
        self.assertEqual(int(baseline['outstanding_mad']),22867875)
        self.assertEqual(int(baseline['over_limit_mad']),3426375)
        self.assertEqual(int(baseline['critical_alerts']),41)

    def test_no_duplicate_scenario_limit_pair(self):
        pairs=[(x['scenario_key'],x['limit_id']) for x in self.rows('fact_scenarios.csv')]
        self.assertEqual(len(pairs),len(set(pairs)))

    def test_alerts_foreign_keys(self):
        limits={x['limit_id'] for x in self.rows('dim_limits.csv')}
        self.assertTrue(all(x['limit_id'] in limits for x in self.rows('fact_alerts.csv')))

if __name__=='__main__': unittest.main()
