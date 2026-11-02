"""Compatibility and consistency tests for the portfolio dashboard."""
import json
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from build_dashboard import prepare_payload, main


class TestDashboardStage2(unittest.TestCase):
    def test_loaded_totals_match_invoice_and_limit_tables(self):
        payload=prepare_payload()
        a=sum(x['outstanding_mad'] for x in payload['limits'])
        b=sum(x['outstanding_mad'] for x in payload['invoices'])
        self.assertEqual(a,b)
        self.assertGreater(a,0)

    def test_aging_buckets_cover_invoice_outstanding(self):
        payload=prepare_payload()
        buckets={'not_due','1-30','31-60','61-90','90+'}
        self.assertTrue(all(x['aging_bucket'] in buckets for x in payload['invoices']))
        self.assertEqual(sum(x['outstanding_mad'] for x in payload['invoices']),
                         sum(x['outstanding_mad'] for x in payload['limits']))

    def test_every_invoice_references_a_known_limit(self):
        payload=prepare_payload()
        refs={x['limit_id'] for x in payload['limits']}
        self.assertTrue(all(x['limit_id'] in refs for x in payload['invoices']))

    def test_rendered_html_contains_data_and_filters(self):
        path=main()
        html=path.read_text(encoding='utf-8')
        self.assertIn('const DATA = ',html)
        self.assertIn('Executive Risk Overview',html)
        self.assertNotIn('/*__PORTFOLIO_DATA__*/',html)
        self.assertIn('id="sector"',html)
        self.assertIn('id="buyers"',html)


if __name__=='__main__':
    unittest.main()
