import fastf1
import fastf1.plotting as fplt
import matplotlib.pyplot as plt

from myutils import *

# Columns: [Time, Driver, DriverNumber, LapTime, LapNumber, Stint, PitOutTime, PitInTime,
#  Sector1Time, Sector2Time, Sector3Time, Sector1SessionTime, Sector2SessionTime, Sector3SessionTime, SpeedI1, SpeedI2, SpeedFL, SpeedST,
#  IsPersonalBest, Compound, TyreLife, FreshTyre, Team, LapStartTime, LapStartDate, TrackStatus, Position, Deleted, DeletedReason, FastF1Generated, IsAccurate
# AirTemp Humidity Pressure Rainfall TrackTemp  WindDirection  WindSpeed]

event = fastf1.get_event(2024, 'Australia', backend='f1timing')

race = event.get_practice(2)
race.load(telemetry=False, weather=False, messages=False)
laps = race.laps

# laps = laps_simplified(race.laps, 'GAS')
# print(laps)

# print(speed_traps(race.laps))

rp = long_runs(laps)
print(rp)

# print(best_times(laps))

# alonso = laps_simplified(laps, 'ALO')

# print(russell)

# xRussell = russell['LapNumber']
# yRussell = russell['LapTimeSeconds']

# print(russell)
# print(russell2)
# print(best_times(laps_simplified(laps)))

# xAlonso = alonso['LapNumber']
# yAlonso = alonso['LapTimeSeconds']

# plt.plot(xRussell, yRussell, label='Russell', color='blue')
# plt.plot(xAlonso, yAlonso, label='Alonso', color='green')
# plt.show()

# TODO - practice theoretical bests, long run pace, speed traps, sector comparison