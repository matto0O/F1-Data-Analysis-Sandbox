import fastf1
import fastf1.plotting as fplt
import matplotlib.pyplot as plt

from myutils import *

# Columns: [Time, Driver, DriverNumber, LapTime, LapNumber, Stint, PitOutTime, PitInTime,
#  Sector1Time, Sector2Time, Sector3Time, Sector1SessionTime, Sector2SessionTime, Sector3SessionTime, SpeedI1, SpeedI2, SpeedFL, SpeedST,
#  IsPersonalBest, Compound, TyreLife, FreshTyre, Team, LapStartTime, LapStartDate, TrackStatus, Position, Deleted, DeletedReason, FastF1Generated, IsAccurate
# AirTemp Humidity Pressure Rainfall TrackTemp  WindDirection  WindSpeed]

event = fastf1.get_event(2024, 'Australia', backend='f1timing')

race = event.get_race()
race.load(telemetry=False, weather=False, messages=False)
laps = race.laps

# TODO - driver comparison, weather support, charts, telemetry
