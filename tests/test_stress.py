"""Regression tests for reproducible static what-if scenarios."""
import unittest
from copy import deepcopy
from build_dashboard import read_csv, prepare_payload
from src.stress import bucket, simulate, scenario_grid, AGING_DAYS, LIMIT_CUTS

class TestStressScenarios(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.limits = read_csv('credit_limits_snapshot.csv')
        cls.invoices = read_csv('invoices_snapshot.csv')
        cls.payload = prepare_payload()
        cls.base = cls.payload['stress']['0_0']

    def test_zero_shock_reconciles_to_snapshot(self):
        summary = self.base['summary']
        self.assertEqual(summary['overdue_30_plus_mad'], 15604500)
        self.assertEqual(summary['over_limit_mad'], 3426375)
        self.assertEqual(summary['outstanding_mad'], 22867875)
        self.assertEqual(summary['critical_alerts'], 41)

    def test_no_mutation_of_snapshots(self):
        lim, inv = deepcopy(self.limits), deepcopy(self.invoices)
        simulate(self.limits,self.invoices,'2026-10-31',60,50)
        self.assertEqual(lim,self.limits)
        self.assertEqual(inv,self.invoices)

    def test_monotonicity_of_both_shocks(self):
        for cut in LIMIT_CUTS:
            previous = -1
            for days in AGING_DAYS:
                late = self.payload['stress'][f'{days}_{cut}']['summary']['overdue_30_plus_mad']
                self.assertGreaterEqual(late,previous)
                previous = late
        for days in AGING_DAYS:
            previous = -1
            for cut in LIMIT_CUTS:
                excess = self.payload['stress'][f'{days}_{cut}']['summary']['over_limit_mad']
                self.assertGreaterEqual(excess,previous)
                previous = excess

    def test_shocks_are_independent(self):
        base = self.payload['stress']['0_0']['summary']
        delayed = self.payload['stress']['60_0']['summary']
        cut = self.payload['stress']['0_50']['summary']
        self.assertEqual(delayed['over_limit_mad'],base['over_limit_mad'])
        self.assertEqual(cut['overdue_30_plus_mad'],base['overdue_30_plus_mad'])
        self.assertEqual(delayed['outstanding_mad'],base['outstanding_mad'])
        self.assertEqual(cut['outstanding_mad'],base['outstanding_mad'])

    def test_grid_is_complete_and_reconciles(self):
        grid=self.payload['stress']
        self.assertEqual(len(grid),30)
        for scenario in grid.values():
            rows=scenario['rows']
            self.assertEqual(len(rows),140)
            self.assertEqual(sum(r['scenario_over_limit_mad'] for r in rows),scenario['summary']['over_limit_mad'])
            self.assertEqual(sum(r['scenario_overdue_30_mad'] for r in rows),scenario['summary']['overdue_30_plus_mad'])

    def test_days_boundary_and_not_due(self):
        self.assertEqual([bucket(x) for x in [-5,0,1,30,31,60,61,90,91]],
                         ['not_due','not_due','1-30','1-30','31-60','31-60','61-90','61-90','90+'])

    def test_invalid_scenario_raises(self):
        with self.assertRaises(ValueError): simulate(self.limits,self.invoices,'2026-10-31',7,0)
        with self.assertRaises(ValueError): simulate(self.limits,self.invoices,'2026-10-31',0,23)

    def test_warning_rules_are_reused(self):
        self.assertEqual({(a['limit_id'],a['score']) for a in self.payload['alerts']},
                         {(r['limit_id'],r['score']) for r in self.base['rows'] if r['score']>0})

    def test_static_html_contains_all_scenarios(self):
        from build_dashboard import main
        text = main().read_text(encoding='utf8')
        self.assertIn('id="viewStress"',text)
        self.assertIn('"60_50"',text)
        self.assertIn('id="sExport"',text)

if __name__ == '__main__': unittest.main()
