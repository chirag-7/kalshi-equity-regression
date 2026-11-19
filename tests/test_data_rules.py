"""Checks for the failure modes that would change this study's meaning."""
import sys
import unittest
from pathlib import Path
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from fit_models import validate
from download_data import candle_url


class DataRules(unittest.TestCase):
    def test_preliminary_panel_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"timestamp_aligned"):
            validate(pd.DataFrame({"timestamp_aligned":[False]}))

    def test_alignment_alone_does_not_prove_quality(self):
        with self.assertRaisesRegex(ValueError,"quote_quality_passed"):
            validate(pd.DataFrame({"timestamp_aligned":[True]}))

    def test_archived_candles_do_not_use_live_route(self):
        url=candle_url("FED-23JUN-T5.25","FED",0,600,1,archived=True)
        self.assertIn("/historical/markets/",url)
        self.assertNotIn("/series/",url)

    def test_unsupported_frequency_is_rejected(self):
        with self.assertRaises(ValueError):
            candle_url("x","x",0,600,5)


if __name__ == "__main__":
    unittest.main()
