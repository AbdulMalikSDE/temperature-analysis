import os
import pandas as pd
import numpy as np

# -------------------------------
# Configuration
# -------------------------------
DATA_FOLDER = r"C:\Users\AbdulMalik\Downloads\New folder\temperatures"

AVG_TEMP_FILE = "average_temp.txt"
RANGE_FILE = "largest_temp_range_station.txt"
STABILITY_FILE = "temperature_stability_stations.txt"

# -------------------------------
# Month → Season mapping
# -------------------------------
SEASON_MAP = {
    "December": "Summer",
    "January": "Summer",
    "February": "Summer",
    "March": "Autumn",
    "April": "Autumn",
    "May": "Autumn",
    "June": "Winter",
    "July": "Winter",
    "August": "Winter",
    "September": "Spring",
    "October": "Spring",
    "November": "Spring",
}

MONTHS = list(SEASON_MAP.keys())

# -------------------------------
# Load & reshape CSV files
# -------------------------------
all_data = []

for file in os.listdir(DATA_FOLDER):
    if file.endswith(".csv"):
        file_path = os.path.join(DATA_FOLDER, file)
        df = pd.read_csv(file_path)

        # Melt monthly columns into rows
        df_melted = df.melt(
            id_vars=["STATION_NAME"],
            value_vars=MONTHS,
            var_name="Month",
            value_name="Temperature"
        )

        df_melted["Season"] = df_melted["Month"].map(SEASON_MAP)
        df_melted["Temperature"] = pd.to_numeric(df_melted["Temperature"], errors="coerce")

        all_data.append(df_melted)

# Safety check
if not all_data:
    raise ValueError("No CSV files loaded.")

# Combine all years
data = pd.concat(all_data, ignore_index=True)

# Remove missing temperatures
data = data.dropna(subset=["Temperature"])

# ======================================================
# 1. Seasonal Average Temperature (ALL stations, ALL years)
# ======================================================
seasonal_avg = data.groupby("Season")["Temperature"].mean()

with open(AVG_TEMP_FILE, "w") as f:
    for season in ["Summer", "Autumn", "Winter", "Spring"]:
        if season in seasonal_avg:
            f.write(f"{season}: {seasonal_avg[season]:.1f}°C\n")

# ======================================================
# 2. Largest Temperature Range per Station
# ======================================================
station_stats = data.groupby("STATION_NAME")["Temperature"].agg(
    max_temp="max",
    min_temp="min"
)

station_stats["range"] = station_stats["max_temp"] - station_stats["min_temp"]

max_range = station_stats["range"].max()
largest_range_stations = station_stats[station_stats["range"] == max_range]

with open(RANGE_FILE, "w") as f:
    for station, row in largest_range_stations.iterrows():
        f.write(
            f"Station {station}: Range {row['range']:.1f}°C "
            f"(Max: {row['max_temp']:.1f}°C, Min: {row['min_temp']:.1f}°C)\n"
        )

# ======================================================
# 3. Temperature Stability (Standard Deviation)
# ======================================================
station_std = data.groupby("STATION_NAME")["Temperature"].std()

min_std = station_std.min()
max_std = station_std.max()

most_stable = station_std[station_std == min_std]
most_variable = station_std[station_std == max_std]

with open(STABILITY_FILE, "w") as f:
    for station, std in most_stable.items():
        f.write(f"Most Stable: Station {station}: StdDev {std:.1f}°C\n")

    for station, std in most_variable.items():
        f.write(f"Most Variable: Station {station}: StdDev {std:.1f}°C\n")

print("Analysis complete. Output files generated:")
print(f"- {AVG_TEMP_FILE}")
print(f"- {RANGE_FILE}")
print(f"- {STABILITY_FILE}")
