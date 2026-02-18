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

def main():
    print("Electricity Price Comparison Tool")
    print("=================================")
    
    # 1. Select Tariff Type
    print("\nSelect Tariff Type:")
    print("1. Simple (Simples)")
    print("2. Bi-hourly (Bi-horário)")
    print("3. Tri-hourly (Tri-horário)")
    
    try:
        tariff_choice = int(input("Choice (1-3): "))
    except ValueError:
        print("Invalid input. Defaulting to Simple.")
        tariff_choice = 1

    tariff_type = 'simple'
    if tariff_choice == 2:
        tariff_type = 'bi-hourly'
    elif tariff_choice == 3:
        tariff_type = 'tri-hourly'

    cycle_type = 'daily'
    if tariff_type != 'simple':
        print("\nSelect Cycle Type:")
        print("1. Daily (Diário)")
        print("2. Weekly (Semanal)")
        try:
            cycle_choice = int(input("Choice (1-2): "))
            if cycle_choice == 2:
                cycle_type = 'weekly'
        except ValueError:
            print("Invalid input. Defaulting to Daily.")

    # 2. Input Consumption Reference
    print("\nConsumption Reference:")
    try:
        ref_kwh = float(input("  Reference Amount (kWh): "))
        ref_month = int(input("  Reference Month (1-12, or 0 for Annual Total): "))
    except ValueError:
        print("Invalid input. Exiting.")
        return

    # Load Profile and Calculate Split
    print("\nLoading Load Profile (BTN C)...")
    csv_path = os.path.join(os.path.dirname(__file__), 'rlp', 'EREDES_2025_BTN_1000kwh_15min.csv')
    
    try:
        tou_consumption = portugal_tou.load_and_calculate_tou(csv_path, cycle_type, ref_kwh, ref_month)
    except FileNotFoundError:
        print(f"Error: Could not find RLP file at {csv_path}")
        return
    except Exception as e:
        print(f"Error processing profile: {e}")
        return

    # Calculate scale for simple comparison (total kWh)
    total_annual_kwh = sum(tou_consumption.values())
    print(f"\nEstimated Annual Consumption: {total_annual_kwh:.2f} kWh")
    if tariff_type != 'simple':
        print("Breakdown per period:")
        for p, val in tou_consumption.items():
            if val > 0:
                print(f"  {p}: {val:.2f} kWh")

    # 3. Contract Details
    num_contracts = 2
    for i in range(1, num_contracts + 1):
        print(f"\nEnter details for Contract {i}:")
        daily_fee = float(input("  Daily fee (€): "))
        
        rates = {}
        if tariff_type == 'simple':
            p = float(input("  Price (€/kWh): "))
            cost = compute_total_cost(p, daily_fee, total_annual_kwh)
        
        elif tariff_type == 'bi-hourly':
            # Peak (Fora de Vazio), Off-Peak (Vazio)
            # Map internal names: Peak+Mid -> Peak(Fora Vazio), Off -> Off
            # Logic: Input Rate Peak (Fora Vazio), Rate Off (Vazio)
            r_peak = float(input("  Price Peak/Fora de Vazio (€/kWh): "))
            r_off = float(input("  Price Off-Peak/Vazio (€/kWh): "))
            
            # Map to our internal periods
            # Peak & Mid-Peak are "Fora de Vazio"
            rates['peak'] = r_peak
            rates['mid_peak'] = r_peak
            rates['off_peak'] = r_off
            rates['super_off_peak'] = r_off # Should be merged already but just in case
            
            cost = get_tou_cost(tou_consumption, rates, daily_fee)
            
        elif tariff_type == 'tri-hourly':
            # Ponta, Cheias, Vazio
            r_peak = float(input("  Price Peak/Ponta (€/kWh): "))
            r_mid = float(input("  Price Mid-Peak/Cheias (€/kWh): "))
            r_off = float(input("  Price Off-Peak/Vazio (€/kWh): "))
            
            rates['peak'] = r_peak
            rates['mid_peak'] = r_mid
            rates['off_peak'] = r_off
            rates['super_off_peak'] = r_off
            
            cost = get_tou_cost(tou_consumption, rates, daily_fee)
            
        print(f"  => Annual Cost: €{cost:.2f}")

if __name__ == "__main__":
    main()
