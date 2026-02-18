import csv
import datetime

class TimeInterval:
    def __init__(self, start, end):
        self.start = float(start)
        self.end = float(end)

    def contains(self, hour_decimal):
        # Handle crossing midnight if needed, but the provided rules usually split at 0
        if self.start <= self.end:
            return self.start <= hour_decimal < self.end
        else:
            # Crosses midnight (e.g. 22 to 2) - Not used in provided rules but good for robustness if needed
            return self.start <= hour_decimal or hour_decimal < self.end

class PortugueseTOUCycle:
    """
    Implementation of Portuguese TOU Cycles (Diário/Semanal).
    """
    def __init__(self, cycle_type='daily'):
        self.cycle_type = cycle_type

    def _is_summer_time(self, dt):
        """
        Determine if it is Summer Time (Hora Legal de Verão).
        Portugal (CET/CEST): Last Sunday March -> Last Sunday Oct.
        Using a simplified rule based on date ranges as requested.
        """
        # Last Sunday of March
        march_31 = datetime.date(dt.year, 3, 31)
        last_sunday_march = march_31 - datetime.timedelta(days=(march_31.weekday() + 1) % 7)
        
        # Last Sunday of October
        oct_31 = datetime.date(dt.year, 10, 31)
        last_sunday_oct = oct_31 - datetime.timedelta(days=(oct_31.weekday() + 1) % 7)

        current_date = dt.date()
        
        # Summer time starts at 1AM UTC on last Sunday of March and ends at 2AM UTC on last Sunday Oct
        # Simplified: Check if date is strictly between
        if last_sunday_march < current_date < last_sunday_oct:
            return True
        elif current_date == last_sunday_march:
             return dt.hour >= 1 # After 1AM
        elif current_date == last_sunday_oct:
             return dt.hour < 2 # Before 2AM
        
        return False

    def _get_intervals(self, is_summer, is_weekend, weekday):
        """
        Returns dictionary of {period_name: [intervals]}
        weekday: 0=Mon, 6=Sun
        """
        intervals = {
            'peak': [],         # Ponta
            'mid_peak': [],     # Cheias
            'off_peak': [],     # Vazio
            'super_off_peak': [] # Super Vazio
        }
        
        if self.cycle_type == 'daily':
            if not is_summer: # Winter
                intervals['peak'] = [TimeInterval(9, 10.5), TimeInterval(18, 20.5)]
                intervals['mid_peak'] = [TimeInterval(8, 9), TimeInterval(10.5, 18), TimeInterval(20.5, 22)]
                intervals['off_peak'] = [TimeInterval(6, 8), TimeInterval(22, 24), TimeInterval(0, 2)]
                intervals['super_off_peak'] = [TimeInterval(2, 6)]
            else: # Summer
                intervals['peak'] = [TimeInterval(10.5, 13), TimeInterval(19.5, 21)]
                intervals['mid_peak'] = [TimeInterval(8, 10.5), TimeInterval(13, 19.5), TimeInterval(21, 22)]
                intervals['off_peak'] = [TimeInterval(6, 8), TimeInterval(22, 24), TimeInterval(0, 2)]
                intervals['super_off_peak'] = [TimeInterval(2, 6)]
                
        elif self.cycle_type == 'weekly':
            is_saturday = (weekday == 5)
            is_sunday = (weekday == 6)
            
            if not is_summer: # Winter
                if not is_weekend: # Mon-Fri
                    intervals['peak'] = [TimeInterval(9.5, 12), TimeInterval(18.5, 21)]
                    intervals['mid_peak'] = [TimeInterval(7, 9.5), TimeInterval(12, 18.5), TimeInterval(21, 24)]
                    intervals['off_peak'] = [TimeInterval(0, 2), TimeInterval(6, 7)]
                    intervals['super_off_peak'] = [TimeInterval(2, 6)]
                elif is_saturday:
                    intervals['mid_peak'] = [TimeInterval(9.5, 13), TimeInterval(18.5, 22)]
                    intervals['off_peak'] = [TimeInterval(0, 2), TimeInterval(6, 9.5), TimeInterval(13, 18.5), TimeInterval(22, 24)]
                    intervals['super_off_peak'] = [TimeInterval(2, 6)]
                elif is_sunday:
                    intervals['off_peak'] = [TimeInterval(0, 2), TimeInterval(6, 24)]
                    intervals['super_off_peak'] = [TimeInterval(2, 6)]
            
            else: # Summer
                if not is_weekend: # Mon-Fri
                    intervals['peak'] = [TimeInterval(9.25, 12.25)]
                    intervals['mid_peak'] = [TimeInterval(7, 9.25), TimeInterval(12.25, 24)]
                    intervals['off_peak'] = [TimeInterval(0, 2), TimeInterval(6, 7)]
                    intervals['super_off_peak'] = [TimeInterval(2, 6)]
                elif is_saturday:
                    intervals['mid_peak'] = [TimeInterval(9, 14), TimeInterval(20, 22)]
                    intervals['off_peak'] = [TimeInterval(0, 2), TimeInterval(6, 9), TimeInterval(14, 20), TimeInterval(22, 24)]
                    intervals['super_off_peak'] = [TimeInterval(2, 6)]
                elif is_sunday:
                    intervals['off_peak'] = [TimeInterval(0, 2), TimeInterval(6, 24)]
                    intervals['super_off_peak'] = [TimeInterval(2, 6)]
        
        return intervals

    def get_period_name(self, dt):
        is_summer = self._is_summer_time(dt)
        weekday = dt.weekday()
        is_weekend = weekday >= 5
        
        intervals_map = self._get_intervals(is_summer, is_weekend, weekday)
        
        current_hour = dt.hour + dt.minute / 60.0
        
        for period_name, intervals in intervals_map.items():
            for interval in intervals:
                if interval.contains(current_hour):
                    return period_name
        
        return 'off_peak'

def load_and_calculate_tou(csv_path, cycle_type, ref_kwh, ref_month):
    """
    Parses the RLP CSV and returns scaled consumption for each TOU period.
    """
    tou_totals = {'peak': 0.0, 'mid_peak': 0.0, 'off_peak': 0.0, 'super_off_peak': 0.0}
    raw_month_total = 0.0
    raw_annual_total = 0.0
    
    cycle = PortugueseTOUCycle(cycle_type)

    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        header = next(reader) 
        # Header: Datetime, BTN A - Wh, BTN B - Wh, BTN C - Wh
        # We assume BTN C is index 3
        
        btn_c_idx = 3

        for row in reader:
            if not row: continue
            dt_str = row[0]
            try:
                # Format: 01/01/2025 00:00
                dt = datetime.datetime.strptime(dt_str, "%d/%m/%Y %H:%M")
            except ValueError:
                continue

            try:
                val = float(row[btn_c_idx])
            except (ValueError, IndexError):
                continue

            raw_annual_total += val
            
            # If ref_month is specified (1-12), track total for that month
            if ref_month > 0 and dt.month == ref_month:
                raw_month_total += val
            
            period = cycle.get_period_name(dt)
            tou_totals[period] += val

    # Calculate scaling factor
    scaling_factor = 1.0
    if ref_month > 0:
        if raw_month_total > 0:
             # Scale so that the specific month matches ref_kwh
             # BUT we want annual estimate. 
             # So we assume the *shape* is correct. 
             # If user consumed X in Jan, and Jan is Y% of total in profile, then Annual = X / Y%.
             # Or simply: Scale everything by (User_Jan / Profile_Jan)
             scaling_factor = (ref_kwh * 1000) / raw_month_total # input kwh -> Wh
        else:
             print(f"Warning: No data found for month {ref_month} in profile.")
    else:
        if raw_annual_total > 0:
             scaling_factor = (ref_kwh * 1000) / raw_annual_total

    # Apply scaling and convert Wh to kWh
    final_totals = {}
    for p, val in tou_totals.items():
        final_totals[p] = (val * scaling_factor) / 1000.0
        
    # Merge Super Off Peak into Off Peak for Residential
    final_totals['off_peak'] += final_totals.pop('super_off_peak', 0)
    
    return final_totals
