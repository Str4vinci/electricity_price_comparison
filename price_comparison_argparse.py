import argparse


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

    :returns: break-even consumption in kWh (float)
    """
    try:
        return (fee2 - fee1) * days / (price1 - price2)
    except ZeroDivisionError:
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Compare two energy contracts and compute break-even consumption"
    )
    parser.add_argument("--price1", type=float, required=True,
                        help="€/kWh for contract 1")
    parser.add_argument("--fee1", type=float, required=True,
                        help="Daily fixed fee (€) for contract 1")
    parser.add_argument("--price2", type=float, required=True,
                        help="€/kWh for contract 2")
    parser.add_argument("--fee2", type=float, required=True,
                        help="Daily fixed fee (€) for contract 2")
    parser.add_argument("--consumption", type=float, required=False,
                        help="Annual consumption in kWh to compare total costs")
    parser.add_argument("--days", type=int, default=365,
                        help="Number of billing days in a year (default: 365)")
    args = parser.parse_args()

    if args.consumption is not None:
        cost1 = compute_total_cost(args.price1, args.fee1, args.consumption, args.days)
        cost2 = compute_total_cost(args.price2, args.fee2, args.consumption, args.days)
        print(f"For annual consumption of {args.consumption} kWh:")
        print(f"  Contract 1: €{cost1:.2f}")
        print(f"  Contract 2: €{cost2:.2f}")
        winner = "1" if cost1 < cost2 else "2" if cost2 < cost1 else "tie"
        if winner != "tie":
            print(f"  => Contract {winner} is cheaper.")
        else:
            print("  => Both contracts cost the same.")

    breakeven = find_break_even(args.price1, args.fee1, args.price2, args.fee2, args.days)
    if breakeven is None:
        print("Cannot compute break-even: the price per kWh is the same for both contracts.")
    else:
        print(f"Break-even consumption: {breakeven:.2f} kWh per year")


if __name__ == "__main__":
    main()

