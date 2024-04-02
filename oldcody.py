import fastf1
import fastf1.plotting as fplt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Columns: [Time, Driver, DriverNumber, LapTime, LapNumber, Stint, PitOutTime, PitInTime,
#  Sector1Time, Sector2Time, Sector3Time, Sector1SessionTime, Sector2SessionTime, Sector3SessionTime, SpeedI1, SpeedI2, SpeedFL, SpeedST,
#  IsPersonalBest, Compound, TyreLife, FreshTyre, Team, LapStartTime, LapStartDate, TrackStatus, Position, Deleted, DeletedReason, FastF1Generated, IsAccurate
# AirTemp Humidity Pressure Rainfall TrackTemp  WindDirection  WindSpeed]

event = fastf1.get_event(2024, 'Bahrain', backend='f1timing')

def free_practice(event, no):
    fp = event.get_practice(no)
    fp.load(telemetry=False)
    laps = fp.laps

    weather = laps.get_weather_data()

    laps.reset_index(drop=True)
    weather = weather.reset_index(drop=True)

    laps['Session'] = f'FP{no}'

    resultingLaps = pd.concat([laps, weather.loc[:, ~(weather.columns == 'Time')]], axis=1)
    return resultingLaps

def friday(event):
    laps = pd.concat([free_practice(event,1), free_practice(event,2)], axis=0)

    laps = laps[laps['PitOutTime'].isna() & laps['PitInTime'].isna()]
    laps = laps[laps['Deleted']==False]

    laps['LapTimeSeconds'] = laps['LapTime'].dt.total_seconds()
    laps['S1'] = laps['Sector1Time'].dt.total_seconds()
    laps['S2'] = laps['Sector2Time'].dt.total_seconds()
    laps['S3'] = laps['Sector3Time'].dt.total_seconds()
    laps['Time'] = laps['Time'].dt.total_seconds()

    laps = laps[['Session','Time', 'Driver', 'LapTimeSeconds', 'LapNumber', 'Stint', 'S1', 'S2', 'S3', 'Compound', 'TyreLife', 'Team', 'TrackStatus', 'Rainfall']]
    return laps.dropna()

for driver, driver_laps in dict(tuple(free_practice(event, 2).groupby('Driver'))).items():
    print("Driver:", driver)

    for compound, driver_compound_laps in dict(tuple(driver_laps.groupby('Driver'))).items():

        q75, q25 = driver_compound_laps['LapTimeSeconds'].quantile(0.75), driver_compound_laps['LapTimeSeconds'].quantile(0.25)

        iqr = q75 - q25

        max_laptime = q75 + 1.5 * iqr
        min_racepace_laptime = q25 - 1.5 * iqr

        driver_compound_laps.loc[driver_compound_laps['LapTimeSeconds'] > max_laptime, 'LapTimeSeconds'] = np.nan
        driver_compound_laps.loc[driver_compound_laps['LapTimeSeconds'] < min_racepace_laptime, 'LapTimeSeconds'] = np.nan
        driver_compound_laps.dropna()

    # print(driver_laps[['LapTimeSeconds', 'S1', 'S2', 'S3', 'Compound']].groupby('Compound').describe())

    best_lap = driver_laps['LapTimeSeconds'].min()
    theoretical_best = (driver_laps['S1'].min() + driver_laps['S2'].min() + driver_laps['S3'].min()).round(3)
    to_gain = (best_lap - theoretical_best).round(3)
    print("Best lap:", best_lap)
    print("Theoretical best lap:", theoretical_best)
    print("To gain:", to_gain)
