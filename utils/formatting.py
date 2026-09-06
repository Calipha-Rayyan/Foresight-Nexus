def format_units(value: float) -> str:
    if value is None:
        return "N/A"
    return f"{value:,.0f}"


def format_currency(value: float, symbol: str = "$") -> str:
    if value is None:
        return "N/A"
    return f"{symbol}{value:,.0f}"


def format_pct(value: float, signed: bool = False) -> str:
    if value is None:
        return "N/A"
    sign = "+" if signed and value >= 0 else ""
    return f"{sign}{value:.1f}%"


def format_days(value: float) -> str:
    if value is None or value == float("inf") or value < 0:
        return "∞"
    return f"{value:.0f} days"
