"""Robustness check: is SwiftRoute's advantage real, or one lucky day?
Runs 10 different random delivery days (40 stops, 4 trucks x 15 packages, Tuesday 9:00)
on real roads + real traffic, and compares with the simple method each time.
Run:  python validate.py   ->  results/validation.csv"""
import os

import pandas as pd

import sample
from plan import run
from traffic import load_profile

profile, source, _ = load_profile()
rows = []
for seed in range(1, 11):
    r = run(sample.DEPOT, sample.make(40, seed=seed), 4, 15, profile, 3, 9, seconds=5)
    s, b = r["smart_kpi"], r["naive_kpi"]
    rows.append({"day (seed)": seed, "SwiftRoute cost": s["Cost ($)"], "Simple cost": b["Cost ($)"],
                 "Saving %": round(100 * (b["Cost ($)"] - s["Cost ($)"]) / b["Cost ($)"], 1),
                 "SwiftRoute delivered": s["Delivered"], "Simple delivered": b["Delivered"],
                 "SwiftRoute on time %": s["On time %"], "Simple on time %": b["On time %"],
                 "SwiftRoute km": s["Total km"], "Simple km": b["Total km"]})
    print("done", seed, rows[-1]["Saving %"], flush=True)
df = pd.DataFrame(rows)
os.makedirs("results", exist_ok=True)
df.to_csv("results/validation.csv", index=False)
print(df.to_string(index=False))
d = df["SwiftRoute on time %"] - df["Simple on time %"]
print(f"\nCost saving: mean {df['Saving %'].mean():.1f}%  (min {df['Saving %'].min():.1f}%, max {df['Saving %'].max():.1f}%)")
print(f"On-time gain: mean {d.mean():+.1f} pts  (min {d.min():+.1f}, max {d.max():+.1f})")
dl = lambda col: df[col].str.split("/").str[0].astype(int)
print(f"Delivered: SwiftRoute mean {dl('SwiftRoute delivered').mean():.1f}/40, simple mean {dl('Simple delivered').mean():.1f}/40")
print(f"SwiftRoute cheaper on {(df['Saving %'] > 0).sum()}/10 days, more on time on {(d > 0).sum()}/10 days")
