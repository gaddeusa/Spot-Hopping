import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Add scripts folder to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

from spot_termination_handler import check_for_interruption, drain_node

class TestTerminationHandler(unittest.TestCase):

    @patch('requests.get')
    def test_no_interruption(self, mock_get):
        """Verify we return False when everything is normal (404)"""
        mock_get.return_value.status_code = 404
        
        result = check_for_interruption()
        self.assertFalse(result)
        print("\n[PASS] No interruption detected (404) -> Handler sleeps.")

    @patch('requests.get')
    @patch('requests.put') # Mock token call
    def test_interruption_detected(self, mock_put, mock_get):
        """Verify we return True when AWS warns us (200 OK)"""
        # Mock Token
        mock_put.return_value.status_code = 200
        mock_put.return_value.text = "TOKEN"

        # Mock Metadata
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "action": "stop",
            "time": "2026-02-19T10:00:00Z"
        }
        
        result = check_for_interruption()
        self.assertTrue(result)
        print("\n[PASS] Interruption detected (200 OK) -> Handler activates!")

    @patch('time.sleep') # Don't actually sleep
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_drain_node_creates_stop_file(self, mock_file, mock_sleep):
        """Verify drain_node creates the specific stop file"""
        drain_node()
        
        # Check if it tried to write to /tmp/stop_working
        mock_file.assert_called_with('/tmp/stop_working', 'w')
        mock_file().write.assert_called_with('STOP')
        print("\n[PASS] Drain signal sent -> Created /tmp/stop_working")

if __name__ == '__main__':
    unittest.main()
