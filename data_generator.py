import random
from datetime import datetime, timedelta

# base_date = 2026-04-27 (Monday)
# day 5  = 2026-05-02 Saturday  → weekend ventilation anomaly
# day 15 = 2026-05-12 Tuesday   → thermostat too high
# day 21 = 2026-05-18 Monday    → unknown load after hours
# day 22 = 2026-05-19 Tuesday   → continues
# day 26 = 2026-05-23 Saturday  → weekend forgotten equipment

ANOMALIES = {
    # (day, hour_min, hour_max): (multiplier, reason)
    (5,  0, 23): (1.9, "Ventilasjonsanlegg ikke skrudd av for helgen"),
    (15, 6, 18): (1.5, "Temperatursettpunkt satt for høyt (23°C)"),
    (21, 17, 23): (1.7, "Ukjent belastning etter stengetid"),
    (22, 17, 23): (1.7, "Ukjent belastning etter stengetid"),
    (26, 0, 23): (1.55, "Teknisk utstyr stående på i helgen"),
}

def generate_energy_data(days=30):
    """Generate realistic synthetic building energy data."""
    random.seed(42)
    data = []
    base_date = datetime(2026, 4, 27, 0, 0)

    for day in range(days):
        date = base_date + timedelta(days=day)
        weekday = date.weekday()
        is_weekend = weekday >= 5
        base_temp = -2 + (day * 0.35) + random.uniform(-2.5, 2.5)

        for hour in range(24):
            dt = date + timedelta(hours=hour)

            if 0 <= hour < 6:
                load_factor = 0.28
            elif 6 <= hour < 9:
                load_factor = 0.65 + (hour - 6) * 0.12
            elif 9 <= hour < 17:
                load_factor = 1.0
            elif 17 <= hour < 21:
                load_factor = 0.72
            else:
                load_factor = 0.38

            if is_weekend:
                load_factor *= 0.45

            temp_factor = 1.0 + max(0, (6 - base_temp)) * 0.022
            normal_baseline = 125 * load_factor * temp_factor

            anomaly = False
            anomaly_reason = None
            multiplier = 1.0

            for (aday, hmin, hmax), (mult, reason) in ANOMALIES.items():
                if day == aday and hmin <= hour <= hmax:
                    multiplier = mult
                    anomaly = True
                    anomaly_reason = reason
                    break

            actual_baseline = normal_baseline * multiplier
            actual = actual_baseline + random.uniform(-4, 4)
            expected = normal_baseline + random.uniform(-4, 4)

            data.append({
                "timestamp": dt.strftime("%Y-%m-%d %H:%M"),
                "date": dt.strftime("%Y-%m-%d"),
                "hour": hour,
                "weekday": date.strftime("%A"),
                "kwh": round(max(0, actual), 1),
                "expected_kwh": round(max(0, expected), 1),
                "temperature_c": round(base_temp, 1),
                "is_anomaly": anomaly,
                "anomaly_reason": anomaly_reason,
                "building": "Bygg A - Kontorbygg Hamar",
            })

    return data


def get_daily_summary(data):
    """Aggregate hourly data into daily summaries."""
    from collections import defaultdict
    days = defaultdict(lambda: {
        "total_kwh": 0, "expected_kwh": 0,
        "anomaly_hours": 0, "anomalies": set(),
        "temps": [], "date": "", "weekday": ""
    })

    for row in data:
        d = row["date"]
        days[d]["total_kwh"] += row["kwh"]
        days[d]["expected_kwh"] += row["expected_kwh"]
        days[d]["temps"].append(row["temperature_c"])
        days[d]["date"] = d
        days[d]["weekday"] = row["weekday"]
        if row["is_anomaly"]:
            days[d]["anomaly_hours"] += 1
            if row["anomaly_reason"]:
                days[d]["anomalies"].add(row["anomaly_reason"])

    result = []
    for d, v in sorted(days.items()):
        deviation_pct = ((v["total_kwh"] - v["expected_kwh"]) / v["expected_kwh"] * 100) if v["expected_kwh"] else 0
        result.append({
            "date": v["date"],
            "weekday": v["weekday"],
            "total_kwh": round(v["total_kwh"], 1),
            "expected_kwh": round(v["expected_kwh"], 1),
            "deviation_pct": round(deviation_pct, 1),
            "avg_temp": round(sum(v["temps"]) / len(v["temps"]), 1),
            "anomaly_hours": v["anomaly_hours"],
            "anomalies": list(v["anomalies"]),
        })

    return result
