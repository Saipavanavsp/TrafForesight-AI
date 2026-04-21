import unittest
import pandas as pd
import numpy as np
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.preprocess import TrafficPreprocessor
from model.predict import predict_traffic

class TestTrafForesight(unittest.TestCase):
    
    def setUp(self):
        self.preprocessor = TrafficPreprocessor()
        self.test_df = pd.DataFrame({
            'day_of_week': [0, 1, 2],
            'hour': [8, 12, 18],
            'weather': [0, 1, 2],
            'speed': [45.0, 30.0, 15.0]
        })

    def test_preprocessor_shape(self):
        """Verify that preprocessed data has correct columns."""
        processed = self.preprocessor.transform(self.test_df)
        expected_cols = ['day_of_week', 'hour', 'weather', 'speed', 'is_weekend', 'is_peak_hour']
        for col in expected_cols:
            self.assertIn(col, processed.columns)

    def test_prediction_output_structure(self):
        """Verify the JSON structure of the prediction result."""
        # Note: requires rf_model.pkl and preprocessor.pkl to exist
        if os.path.exists('model/rf_model.pkl'):
            result = predict_traffic(1, 10, 0, 50.0)
            self.assertIn('predicted_traffic', result)
            self.assertIn('congestion_level', result)
            self.assertIn('forecast', result)
            self.assertIn('anomaly', result)
        else:
            self.skipTest("Model files missing for prediction test.")

    def test_cyclic_logic(self):
        """Test if the internal math for peak hours is correct."""
        # 9 AM should be peak
        processed = self.preprocessor.transform(pd.DataFrame({'day_of_week':[1], 'hour':[9], 'weather':[0], 'speed':[40]}))
        self.assertEqual(processed['is_peak_hour'].iloc[0], 1)
        
        # 2 PM should not be peak
        processed = self.preprocessor.transform(pd.DataFrame({'day_of_week':[1], 'hour':[14], 'weather':[0], 'speed':[40]}))
        self.assertEqual(processed['is_peak_hour'].iloc[0], 0)

if __name__ == '__main__':
    unittest.main()
