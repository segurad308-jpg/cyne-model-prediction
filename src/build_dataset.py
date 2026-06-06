"""
Build dataset Greifensee
"""

import numpy as np
import pandas as pd

INPUT    = "data/raw/ctd_meteo_SPC_2019to2021_0to8m.csv"
OUTPUT   = "data/processed/dataset.csv"
QUANTILE = 0.75 

FEATURES = [
    "mean_temp",          
    "mean_schmidt",       
    "mean_par",          
    "windspeed_mean",     
    "precipitation_tot", 
    "month_sin",         
    "month_cos",
]

df = pd.read_csv(INPUT, parse_dates=["date"])

df["month_sin"] = np.sin(2 * np.pi * df["date"].dt.month / 12)
df["month_cos"] = np.cos(2 * np.pi * df["date"].dt.month / 12)

df = df.dropna(subset=FEATURES + ["mean_phy"]).reset_index(drop=True)

threshold = df["mean_phy"].quantile(QUANTILE)
df["target"] = (df["mean_phy"] >= threshold).astype(int)

df = df[["date", "mean_phy", "target"] + FEATURES]

df.to_csv(OUTPUT, index=False)

print(f"dataset.csv : {df.shape[0]} rows, {df.shape[1]} cols")
print(f"Threshold phycocyanine : {threshold:.2f}")
print(f"Taux de positifs   : {df['target'].mean():.1%}")