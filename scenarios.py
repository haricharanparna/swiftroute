"""Scenario analysis ("what if?"). Used by the app, or run alone:  python scenarios.py"""
import os
import pandas as pd
import sample
from plan import run

CASES = {
    "Normal day (40 stops, 4 trucks, leave 9am)": dict(n=40, trucks=4, hour=9),
    "+1 truck":                                    dict(n=40, trucks=5, hour=9),
    "Traffic 30% worse":                           dict(n=40, trucks=4, hour=9, worse=0.3),
    "Leave at 7am (same customers)":               dict(n=40, trucks=4, hour=7),
    "Orders double (80 stops)":                    dict(n=80, trucks=4, hour=9),
    "Orders double + 4 more trucks":               dict(n=80, trucks=8, hour=9),
}


def run_all(profile, day=3, capacity=15, seconds=10, progress=None):
    rows = []
    for i, (name, c) in enumerate(CASES.items()):
        r = run(sample.DEPOT, sample.make(c["n"]), c["trucks"], capacity, profile, day,
                c["hour"], c.get("worse", 0.0), seconds)
        s, b = r["smart_kpi"], r["naive_kpi"]
        rows.append({"Scenario": name, "Trucks": s["Trucks used"], "Delivered": s["Delivered"],
                     "On time %": s["On time %"], "Km": s["Total km"], "Cost ($)": s["Cost ($)"],
                     "CO2 (kg)": s["CO2 (kg)"],
                     "Simple method on time %": b["On time %"], "Simple method cost ($)": b["Cost ($)"]})
        if progress:
            progress(i + 1, len(CASES), name)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    from traffic import load_profile
    profile, source = load_profile()
    print("Traffic data:", source)
    df = run_all(profile, progress=lambda i, n, name: print(f"done {i}/{n}: {name}"))
    os.makedirs("results", exist_ok=True)
    df.to_csv("results/scenarios.csv", index=False)
    pd.set_option("display.width", 250)
    print(df.to_string(index=False))
