import argparse
import sys
import os

# Ensure local modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import portugal_tou

def compute_total_cost(price_per_kwh, daily_fee, annual_consumption, days=365):
    """
    Calculate the annual total cost for a simple contract.
    """
    return price_per_kwh * annual_consumption + daily_fee * days

def get_tou_cost(tou_consumption, rates, daily_fee, days=365):
    """
    Calculate annual cost for TOU contract.
    tou_consumption: dict of {period: kWh}
    rates: dict of {period: €/kWh}
    """
    energy_cost = 0.0
    for period, kwh in tou_consumption.items():
        rate = rates.get(period, 0.0)
        energy_cost += kwh * rate
    
    fixed_cost = daily_fee * days
    return energy_cost + fixed_cost

def find_break_even(price1, fee1, price2, fee2, days=365):
    """
    Solve for consumption level at which both contracts cost the same (Simple Tariff).
    """
    try:
        if price1 == price2:
            return None
        return (fee2 - fee1) * days / (price1 - price2)
    except ZeroDivisionError:
        return None

def main():
    parser = argparse.ArgumentParser(
        description="Compare two energy contracts (Simple or TOU) and compute cost."
    )
    
    # Common arguments
    parser.add_argument("--days", type=int, default=365,
                        help="Number of billing days in a year (default: 365)")
    
    # Contract 1
    parser.add_argument("--tariff-type", choices=['simple', 'bi-hourly', 'tri-hourly'], default='simple',
                        help="Tariff type for comparisons (default: simple)")
    parser.add_argument("--cycle", choices=['daily', 'weekly'], default='daily',
                        help="Cycle type for TOU tariffs (default: daily)")

    parser.add_argument("--price1", type=float, nargs='+', required=True,
                        help="Price(s) (€/kWh) for Contract 1. Simple: 1 val. Bi: Peak, Off. Tri: Peak, Mid, Off.")
    parser.add_argument("--fee1", type=float, required=True,
                        help="Daily fixed fee (€) for Contract 1")
    
    # Contract 2
    parser.add_argument("--price2", type=float, nargs='+', required=True,
                        help="Price(s) (€/kWh) for Contract 2. Matches tariff-type structure.")
    parser.add_argument("--fee2", type=float, required=True,
                        help="Daily fixed fee (€) for Contract 2")

    # Consumption Reference
    parser.add_argument("--ref-kwh", type=float, required=False,
                        help="Reference consumption amount (kWh). Required for TOU or Cost Calculation.")
    parser.add_argument("--ref-month", type=int, default=0,
                        help="Reference month (1-12) or 0 for Annual. Required for TOU.")

    # Backward compatibility alias
    parser.add_argument("--consumption", type=float, required=False, help=argparse.SUPPRESS)

    args = parser.parse_args()

    # Handle alias
    if args.ref_kwh is None and args.consumption is not None:
        args.ref_kwh = args.consumption

    # Calculate effective annual kWh
    effective_annual_kwh = 0.0

    if args.tariff_type != 'simple':
        if args.ref_kwh is None:
             print("Error: --ref-kwh is required for TOU tariffs.")
             sys.exit(1)
        
        # Load TOU Profile
        print(f"Loading Load Profile (BTN C) for {args.tariff_type} {args.cycle}...")
        csv_path = os.path.join(os.path.dirname(__file__), 'rlp', 'EREDES_2025_BTN_1000kwh_15min.csv')
        try:
            tou_consumption = portugal_tou.load_and_calculate_tou(csv_path, args.cycle, args.ref_kwh, args.ref_month)
        except Exception as e:
            print(f"Error loading profile: {e}")
            sys.exit(1)
            
        effective_annual_kwh = sum(tou_consumption.values())
        print(f"Estimated Annual Consumption: {effective_annual_kwh:.2f} kWh")

        # Map rates
        # Bi: Peak, Off
        # Tri: Peak, Mid, Off
        
        def map_rates(rates_list, t_type):
            r = {}
            if t_type == 'bi-hourly':
                if len(rates_list) < 2:
                    print("Error: Bi-hourly requires 2 rates (Peak, Off).")
                    sys.exit(1)
                r['peak'] = rates_list[0]
                r['mid_peak'] = rates_list[0]
                r['off_peak'] = rates_list[1]
                r['super_off_peak'] = rates_list[1]
            elif t_type == 'tri-hourly':
                if len(rates_list) < 3:
                     print("Error: Tri-hourly requires 3 rates (Peak, Mid, Off).")
                     sys.exit(1)
                r['peak'] = rates_list[0]
                r['mid_peak'] = rates_list[1]
                r['off_peak'] = rates_list[2]
                r['super_off_peak'] = rates_list[2]
            return r

        rates1 = map_rates(args.price1, args.tariff_type)
        rates2 = map_rates(args.price2, args.tariff_type)
        
        cost1 = get_tou_cost(tou_consumption, rates1, args.fee1, args.days)
        cost2 = get_tou_cost(tou_consumption, rates2, args.fee2, args.days)
        
    else:
        # Simple Tariff
        if len(args.price1) != 1 or len(args.price2) != 1:
            print("Error: Simple tariff requires exactly 1 price per contract.")
            sys.exit(1)

        p1 = args.price1[0]
        p2 = args.price2[0]
        
        if args.ref_kwh is not None:
            effective_annual_kwh = args.ref_kwh
            cost1 = compute_total_cost(p1, args.fee1, effective_annual_kwh, args.days)
            cost2 = compute_total_cost(p2, args.fee2, effective_annual_kwh, args.days)
        else:
            cost1 = None
            cost2 = None
            
            # Break even
            breakeven = find_break_even(p1, args.fee1, p2, args.fee2, args.days)
            if breakeven is None:
                print("Cannot compute break-even: prices are equal.")
            else:
                print(f"Break-even consumption: {breakeven:.2f} kWh per year")

    if cost1 is not None and cost2 is not None:
        print(f"For estimated annual consumption of {effective_annual_kwh:.2f} kWh:")
        print(f"  Contract 1: €{cost1:.2f}")
        print(f"  Contract 2: €{cost2:.2f}")
        winner = "1" if cost1 < cost2 else "2" if cost2 < cost1 else "tie"
        if winner != "tie":
            print(f"  => Contract {winner} is cheaper.")
        else:
            print("  => Both contracts cost the same.")

if __name__ == "__main__":
    main()

