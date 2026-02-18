import unittest
import datetime
import sys
import os

# Ensure local modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from portugal_tou import PortugueseTOUCycle, TimeInterval

class TestPortugueseTOU(unittest.TestCase):
    def setUp(self):
        self.daily_cycle = PortugueseTOUCycle('daily')
        self.weekly_cycle = PortugueseTOUCycle('weekly')

    def test_summer_time(self):
        # 2025 DST: Starts March 30 (Sunday), Ends Oct 26 (Sunday)
        
        # Winter: Jan 1
        dt_winter = datetime.datetime(2025, 1, 1, 12, 0)
        self.assertFalse(self.daily_cycle._is_summer_time(dt_winter))

        # Summer: July 1
        dt_summer = datetime.datetime(2025, 7, 1, 12, 0)
        self.assertTrue(self.daily_cycle._is_summer_time(dt_summer))
        
        # Boundary Start: March 30, 2025
        # Before 1AM UTC = Winter
        dt_before = datetime.datetime(2025, 3, 30, 0, 59)
        self.assertFalse(self.daily_cycle._is_summer_time(dt_before))
        # After 1AM UTC = Summer
        dt_after = datetime.datetime(2025, 3, 30, 1, 1)
        self.assertTrue(self.daily_cycle._is_summer_time(dt_after))

    def test_daily_cycle_periods(self):
        # Winter Usage
        # Peak: 09:00-10:30, 18:00-20:30
        # Off-Peak: 22:00-08:00 (Includes Super Off Peak 02-06, and Off Peak 06-08, 22-02)
        # Mid-Peak: Rest
        
        # 2025-01-08 (Wednesday) - Winter
        dt = datetime.datetime(2025, 1, 8, 9, 15) # Peak
        self.assertEqual(self.daily_cycle.get_period_name(dt), 'peak')
        
        dt = datetime.datetime(2025, 1, 8, 19, 0) # Peak
        self.assertEqual(self.daily_cycle.get_period_name(dt), 'peak')

        dt = datetime.datetime(2025, 1, 8, 4, 0) # Super Off Peak
        self.assertEqual(self.daily_cycle.get_period_name(dt), 'super_off_peak')
        
        dt = datetime.datetime(2025, 1, 8, 7, 0) # Off Peak
        self.assertEqual(self.daily_cycle.get_period_name(dt), 'off_peak')
        
        dt = datetime.datetime(2025, 1, 8, 14, 0) # Mid Peak
        self.assertEqual(self.daily_cycle.get_period_name(dt), 'mid_peak')

    def test_weekly_cycle_periods(self):
        # Summer Usage
        # Mon-Fri: Peak 09:15-12:15
        # 2025-07-02 (Wednesday)
        
        dt = datetime.datetime(2025, 7, 2, 10, 0) # Peak
        self.assertEqual(self.weekly_cycle.get_period_name(dt), 'peak')
        
        dt = datetime.datetime(2025, 7, 2, 8, 0) # Mid Peak
        self.assertEqual(self.weekly_cycle.get_period_name(dt), 'mid_peak')

        # Saturday
        # 2025-07-05
        # Off Peak: 14:00-20:00
        dt = datetime.datetime(2025, 7, 5, 15, 0)
        self.assertEqual(self.weekly_cycle.get_period_name(dt), 'off_peak')

        # Sunday
        # 2025-07-06
        # All day Off Peak (except 0-2 and 2-6 mapping, but generally low cost)
        dt = datetime.datetime(2025, 7, 6, 12, 0)
        # Should be off_peak or super_off_peak
        p = self.weekly_cycle.get_period_name(dt)
        self.assertTrue(p in ['off_peak', 'super_off_peak'])

if __name__ == '__main__':
    unittest.main()
