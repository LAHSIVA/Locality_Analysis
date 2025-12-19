# Finance Logic Only

def calculate_financials(locality, max_payback=None, min_roi=None):
    annual_rent = locality.avg_monthly_rent * 12
    maintenance_cost = annual_rent * 0.10
    net_annual_rent = annual_rent - maintenance_cost

    property_value = locality.avg_price_per_sqft * locality.standard_property_size_sqft

    payback_years = property_value / net_annual_rent

    appreciation_rate = 0.05
    appreciated_value = property_value * ((1 + appreciation_rate) ** 10)
    appreciation_gain = appreciated_value - property_value

    total_rental_income = net_annual_rent * 10
    total_gain = total_rental_income + appreciation_gain
    roi_percent = (total_gain / property_value) * 100

    if max_payback is not None and payback_years > max_payback:
        return None

    if min_roi is not None and roi_percent < min_roi:
        return None

    return {
        "name": locality.name,
        "latitude": locality.latitude,
        "longitude": locality.longitude,
        "payback_period_years": round(payback_years, 1),
        "ten_year_roi_percent": round(roi_percent, 2)
    }
