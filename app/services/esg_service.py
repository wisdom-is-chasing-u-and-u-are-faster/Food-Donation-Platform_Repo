"""
ESG Sustainability Analytics & Carbon-Offset Engine
Standard EPA Waste Reduction Model (WARM) factors:
- 1 lb food waste avoided = 1.90 kg CO2 equivalent greenhouse gas emissions prevented
- 1 lb food rescued = 2.50 gallons freshwater footprint conserved
- 1.2 lbs food rescued = 1 wholesome meal equivalent (0.833 meals / lb)
"""
from typing import Dict, Any, List
from app.db.session import query_db


def calculate_esg_metrics() -> Dict[str, Any]:
    """Computes aggregate sustainability metrics from donations and rollups."""
    # Sum from completed/in-transit donations
    don_stats = query_db(
        "SELECT SUM(weight_lbs) as total_lbs FROM donations WHERE status != 'REJECTED'",
        one=True)
    total_lbs = (don_stats["total_lbs"] or 0.0) + \
        164950.0  # Include historical baseline

    co2_kg = round(total_lbs * 1.90, 2)
    water_gal = round(total_lbs * 2.50, 2)
    meals = int(total_lbs * 0.8333)
    # ~11.5 kg CO2/day per passenger vehicle
    cars_off_road_days = round(co2_kg / 11.5, 1)

    history = query_db(
        "SELECT month_year, rescued_weight_lbs, co2_offset_kg, meals_provided FROM esg_analytics ORDER BY month_year ASC")

    return {
        "total_rescued_lbs": total_lbs,
        "co2_emissions_avoided_kg": co2_kg,
        "water_saved_gallons": water_gal,
        "equivalent_vehicles_off_road_days": cars_off_road_days,
        "meals_served": meals,
        "historical_monthly_data": [dict(h) for h in history]
    }
