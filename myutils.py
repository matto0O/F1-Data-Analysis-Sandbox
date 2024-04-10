import fastf1.core as core
import pandas as pd
import numpy as np


def laps_simplified(laps: core.Laps, driverTag=None) -> core.Laps:
    driver = laps.pick_driver(driverTag) if driverTag else laps

    driver['LapTimeSeconds'] = driver['LapTime'].dt.total_seconds()
    driver['S1'] = driver['Sector1Time'].dt.total_seconds()
    driver['S2'] = driver['Sector2Time'].dt.total_seconds()
    driver['S3'] = driver['Sector3Time'].dt.total_seconds()
    driver['Time'] = driver['Time'].dt.total_seconds()

    driver = driver[['Driver', 'LapTimeSeconds', 'LapNumber', 'Stint', 'S1', 'S2', 'S3', 'Compound', 'TyreLife']]
    return driver.dropna()

def theoretical_best(laps: core.Laps) -> tuple:
    purpleS1 = laps['S1'].min()
    purpleS2 = laps['S2'].min()
    purpleS3 = laps['S3'].min()
    
    return purpleS1, purpleS2, purpleS3, (purpleS1 + purpleS2 + purpleS3)

def remove_cruising(laps: core.Laps) -> core.Laps:
    df = pd.DataFrame()
    for driver in laps.groupby('Driver'):
        df = pd.concat([df, driver[1][driver[1]['LapTimeSeconds'] <= 1.15 * driver[1]['LapTimeSeconds'].min()]])
    return df

def remove_pitstops(laps: core.Laps) -> core.Laps:
    laps = laps[laps['PitOutTime'].isnull()]
    laps = laps[laps['PitInTime'].isnull()]
    return laps

def remove_safetycar(laps: core.Laps) -> core.Laps:
    laps = laps[(laps['TrackStatus'] == '1') | (laps['TrackStatus'] == '2')]
    return laps

def filter_outliers(laps: core.Laps) -> core.Laps:
    laps = remove_cruising(laps)
    q75, q25 = laps['LapTimeSeconds'].quantile(0.75), laps['LapTimeSeconds'].quantile(0.25)
    iqr = q75 - q25

    max_laptime = q75 + 1.5 * iqr
    min_racepace_laptime = q25 - 1.5 * iqr

    laps.loc[laps['LapTimeSeconds'] > max_laptime, 'LapTimeSeconds'] = np.nan
    laps.loc[laps['LapTimeSeconds'] < min_racepace_laptime, 'LapTimeSeconds'] = np.nan
    return laps.dropna()

def best_times(laps: core.Laps) -> pd.DataFrame:
    result = pd.DataFrame(columns=['BestS1', 'BestS2', 'BestS3', 'BestTime', 'TheoreticalBest', 'ToGain'])
    for driver in laps.groupby('Driver'):
        bestS1, bestS2, bestS3, tb = theoretical_best(driver[1])
        bestTime = driver[1]['LapTimeSeconds'].min()

        result = pd.concat(
            [
                result,
                pd.DataFrame({
                    'BestS1': bestS1,
                    'BestS2': bestS2,
                    'BestS3': bestS3,
                    'BestTime': bestTime,
                    'TheoreticalBest': tb,
                    'ToGain': abs(round(bestTime - tb, 3))
                }, index=[driver[0]])
            ]
        )

    result.sort_values(by='TheoreticalBest', inplace=True)
    result['OrderChange'] = result['BestTime'].rank(ascending=True) - result['TheoreticalBest'].rank(ascending=True)
    return result

def long_runs(laps: core.Laps) -> pd.DataFrame:
    if not "LapTimeSeconds" in laps.columns:
        laps = laps_simplified(laps)

    FAST_LAPS_THRESHOLD = 0.8

    result = pd.DataFrame(columns=['AverageLapTime', 'AverageS1', 'AverageS2', 'AverageS3', 'Compound'])
    lapsCopy = laps.copy()
    lapsCopy = filter_outliers(lapsCopy)
    for info in lapsCopy.groupby(['Driver', 'Stint']):
        driver = info[1]
        if len(driver) > FAST_LAPS_THRESHOLD * (driver['LapNumber'].max() - driver['LapNumber'].min()):
            newStintDataFrame = pd.DataFrame\
            (
                {
                    'AverageLapTime': round(driver['LapTimeSeconds'].mean(), 3),
                    'AverageS1': round(driver['S1'].mean(), 3),
                    'AverageS2': round(driver['S2'].mean(), 3),
                    'AverageS3': round(driver['S3'].mean(), 3),
                    'Compound': driver['Compound'].iloc[0],
                    'Stint': driver['Stint'].iloc[0],
                    'StintLength': len(driver),
                    'StartTyreWear': driver['TyreLife'].iloc[0]
                }, 
                index=[info[0][0]]
            )
            
            result = pd.concat([result,newStintDataFrame])

    result.sort_values(by='AverageLapTime', inplace=True)
    return result[result['StintLength'] >= 5]

def race_pace(laps: core.Laps, orderBy: str = "AverageLapTime") -> pd.DataFrame:
    #laps = remove_pitstops(laps)
    #laps = remove_safetycar(laps)

    if not "LapTimeSeconds" in laps.columns:
        laps = laps_simplified(laps)

    result = pd.DataFrame(columns=['AverageLapTime', 'AverageS1', 'AverageS2', 'AverageS3', 'TyreDeg', 'Stint', 'StartLap', 'EndLap', 'Compound', 'StartTyreWear', 'StintLength'])
    lapsCopy = laps.copy()

    for info in lapsCopy.groupby(['Driver', 'Stint']):
        driver = info[1]
        stintLen = len(driver)
        lapsFiltered = remove_cruising(driver)
        properLapCount = len(lapsFiltered)
        newStintDataFrame = pd.DataFrame\
        (
            {
                'AverageLapTime': round(lapsFiltered['LapTimeSeconds'].mean(), 3),
                'AverageS1': round(lapsFiltered['S1'].mean(), 3),
                'AverageS2': round(lapsFiltered['S2'].mean(), 3),
                'AverageS3': round(lapsFiltered['S3'].mean(), 3),
                'TyreDeg': round((lapsFiltered['LapTimeSeconds'].max() - lapsFiltered['LapTimeSeconds'].min()) / properLapCount, 3),
                'Stint': int(info[0][1]),
                'Compound': driver['Compound'].iloc[0],
                'StartTyreWear': int(driver['TyreLife'].iloc[0]),
                'StintLength': stintLen,
                'StartLap': int(driver['LapNumber'].min()),
                'EndLap': int(driver['LapNumber'].max())
            }, 
            index=[info[0][0]]
        )
        
        result = pd.concat([result,newStintDataFrame])

    result.sort_values(by=orderBy, inplace=True)
    return result

def speed_traps(laps: core.Laps) -> pd.DataFrame:
    result = pd.DataFrame(columns=['SpeedTrap'])
    for driver in laps.groupby('Driver'):
        result = pd.concat(
            [
                result,
                pd.DataFrame({
                    'SpeedTrap': max([driver[1]['SpeedFL'].max(), driver[1]['SpeedST'].max(), driver[1]['SpeedI1'].max(), driver[1]['SpeedI2'].max()]),
                }, index=[driver[0]])
            ]
        )
    result.sort_values(by='SpeedTrap', ascending=False, inplace=True)
    return result