"""Stage 3: deterministic and explainable alert business rules."""
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.alerts import build_alerts
from build_dashboard import prepare_payload


def line(**kwargs):
    base={'limit_id':'L1','buyer_id':'B1','policyholder_id':'H1','sector':'Automobile',
          'region':'Rabat','risk_band':'low','status':'active',
          'credit_limit_mad':100_000,'outstanding_mad':20_000,
          'overdue_30_plus_mad':0}
    return {**base, **kwargs}


def invoice(**kwargs):
    return {'limit_id':'L1','aging_bucket':'not_due','outstanding_mad':20_000, **kwargs}


class TestStage3Alerts(unittest.TestCase):
    def test_no_alert_without_signal(self):
        self.assertEqual(build_alerts([line()], [invoice()]), [])

    def test_high_synthetic_profile_alone_does_not_trigger_alert(self):
        self.assertEqual(build_alerts([line(risk_band='high')], [invoice()]), [])

    def test_over_limit_rule(self):
        items=build_alerts([line(outstanding_mad=120_000)], [invoice(outstanding_mad=120_000)])
        self.assertEqual(len(items),1)
        self.assertEqual(items[0]['priority'],'high')
        self.assertEqual(items[0]['over_limit_mad'],20_000)
        self.assertEqual([r['code'] for r in items[0]['reasons']],['over_limit'])

    def test_90_plus_rule_requires_amount_and_share(self):
        items=build_alerts([line(outstanding_mad=100_000)], [invoice(outstanding_mad=25_000,aging_bucket='90+')])
        self.assertEqual(items[0]['score'],3)
        self.assertEqual(items[0]['priority'],'watch')
        self.assertEqual(items[0]['overdue_90_plus_mad'],25_000)

    def test_suspended_limit_with_positive_exposure(self):
        items=build_alerts([line(status='suspended')], [invoice()])
        self.assertEqual(items[0]['score'],2)
        self.assertEqual(items[0]['priority'],'watch')

    def test_zero_exposure_is_not_flagged(self):
        self.assertEqual(build_alerts([line(outstanding_mad=0,status='suspended')], []), [])

    def test_payload_alerts_reconcile_with_limit_exposures(self):
        payload=prepare_payload()
        amounts={x['limit_id']:x['outstanding_mad'] for x in payload['limits']}
        for alert in payload['alerts']:
            self.assertEqual(alert['outstanding_mad'],amounts[alert['limit_id']])
            self.assertEqual(alert['score'],sum(r['points'] for r in alert['reasons']))
            self.assertTrue(alert['reasons'])

    def test_alert_list_is_sorted(self):
        payload=prepare_payload()
        keys=[(-a['score'],-a['outstanding_mad'],a['limit_id']) for a in payload['alerts']]
        self.assertEqual(keys,sorted(keys))


if __name__=='__main__':
    unittest.main()
