def compute_total_cost(price_per_kwh, daily_fee, annual_consumption, days=365):
    """
    Calculate the annual total cost for a contract.

    :param price_per_kwh: Price in €/kWh
    :param daily_fee: Daily fixed fee in €
    :param annual_consumption: Annual energy consumption in kWh
    :param days: Number of billing days in a year (default 365)
    :return: Total annual cost in €
    """
    return price_per_kwh * annual_consumption + daily_fee * days


def find_break_even(price1, fee1, price2, fee2, days=365):
    """
    Solve for consumption level at which both contracts cost the same:
    price1 * C + fee1*days = price2*C + fee2*days --> C = (fee2 - fee1)*days / (price1 - price2)

    :returns: break-even consumption in kWh (float) or None if prices equal
    """
    if price1 == price2:
        return None
    return (fee2 - fee1) * days / (price1 - price2)


def main():
    # Prompt user for contract details
    print("Enter details for Contract 1:")
    price1 = float(input("  Price (€/kWh): "))
    fee1 = float(input("  Daily fee (€): "))

    print("\nEnter details for Contract 2:")
    price2 = float(input("  Price (€/kWh): "))
    fee2 = float(input("  Daily fee (€): "))

    # Optional: compare at specific consumption
    resp = input("\nWould you like to compare at a specific annual consumption? (y/n): ").strip().lower()
    if resp == 'y':
        consumption = float(input("  Annual consumption (kWh): "))
        days = 365
        cost1 = compute_total_cost(price1, fee1, consumption, days)
        cost2 = compute_total_cost(price2, fee2, consumption, days)
        print(f"\nFor annual consumption of {consumption:.2f} kWh:")
        print(f"  Contract 1: €{cost1:.2f}")
        print(f"  Contract 2: €{cost2:.2f}")
        if cost1 < cost2:
            print("  => Contract 1 is cheaper.")
        elif cost2 < cost1:
            print("  => Contract 2 is cheaper.")
        else:
            print("  => Both contracts cost the same.")

    # Compute break-even
    breakeven = find_break_even(price1, fee1, price2, fee2)
    if breakeven is None:
        print("\nCannot compute break-even: the price per kWh is the same for both contracts.")
    else:
        print(f"\nBreak-even consumption: {breakeven:.2f} kWh per year")

if __name__ == "__main__":
    main()

