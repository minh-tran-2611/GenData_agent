"""Growth-curve math shared by the simulator and segment agent.

Turns the user-configured GrowthConfig (start volume, monthly growth rate,
plateau month, new-user ratio) into concrete per-day expectations so segment
agents plan against a real growth trajectory instead of guessing freely.
"""
from models import GrowthConfig


def month_index_for_day(day: int) -> int:
    """0-based business month for a 1-based simulation day."""
    return max(0, (day - 1) // 30)


def effective_month(day: int, g: GrowthConfig) -> int:
    """Month index clamped so growth stops compounding after the plateau."""
    plateau = max(1, g.plateau_at_month)
    return min(month_index_for_day(day), plateau - 1)


def expected_total_orders_for_day(day: int, g: GrowthConfig) -> float:
    """Whole-business expected orders for a given day, following the growth curve."""
    em = effective_month(day, g)
    base = max(0, g.start_orders_per_day)
    rate = max(-0.99, g.monthly_growth_rate)
    return base * ((1.0 + rate) ** em)


def expected_total_orders_over(start_day: int, period_days: int, g: GrowthConfig) -> float:
    """Sum of expected whole-business orders across a period (handles intra-period growth)."""
    return sum(expected_total_orders_for_day(start_day + d, g) for d in range(max(1, period_days)))


def growth_stage_for_day(day: int, g: GrowthConfig) -> str:
    """Map a day to a growth stage label, tied to the configured plateau."""
    mi = month_index_for_day(day)
    plateau = max(1, g.plateau_at_month)
    if mi >= plateau:
        return "plateau"
    if mi == 0:
        return "early"
    if mi >= max(1, plateau - 2):
        return "stable"
    return "growing"
