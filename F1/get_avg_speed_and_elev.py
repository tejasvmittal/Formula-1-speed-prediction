import numpy as np
import pandas as pd
from collections import defaultdict

circuit = pd.read_csv('./circuit_info_with_angle.csv')
telemetry = pd.read_csv('./telemetry.csv')

circuits = ['Abu Dhabi', 'Australia', 'Austria', 'Azerbaijan', 'Bahrain', 'Belgium',
 'Brazil', 'Canada', 'Emilia Romagna', 'France', 'Great Britain', 'Hungary',
 'Italy', 'Japan', 'Mexico', 'Miami', 'Monaco', 'Netherlands', 'Saudi Arabia',
 'Singapore', 'Spain', 'United States', 'Las Vegas', 'China']

years = [2022, 2023, 2024]
teams = ['Red Bull Racing', 'Mercedes', 'McLaren', 'Ferrari', 'Aston Martin', 'Haas F1 Team', 'Alpine', 'Williams', 'Kick Sauber', 'RB']


avg_speed = defaultdict(lambda: defaultdict(list))
elevation_change = defaultdict(lambda: defaultdict(list))

for y in years:
    for team in teams:
        for c in circuits:
            df_corners = circuit[circuit['Track'] == c]
            df_positions = telemetry[(telemetry['Track'] == c) & (telemetry['Team'] == team) & (telemetry['Year'] == y)]
            if df_positions.empty:
                continue

            # Initialize cumulative angle for each corner
            corner_angles = {corner: 0 for corner in df_corners['Corner Number'].unique()}

            for corner_num in corner_angles:
                # Get the corner information
                corner_info = df_corners[df_corners['Corner Number'] == corner_num].iloc[0]
                corner_start = np.array([corner_info['X'], corner_info['Y']])
                start_distance = corner_info['Start Distance']
                end_distance = corner_info['End Distance']

                # Filter the position data for this corner
                positions = df_positions[(df_positions['Distance'] >= start_distance) & (df_positions['Distance'] <= end_distance)]
                if positions.empty:
                    continue
                
                for i in range(len(positions)):
                    avg_speed[c][corner_num].append(positions.iloc[i]['Speed'])
                elevation_change[c][corner_num].append(positions.iloc[len(positions)-1]['Z'] - positions.iloc[0]['Z'])

print(avg_speed)
print(elevation_change)

for c in avg_speed:
    for corner in avg_speed[c]:
        avg_speed[c][corner] = np.mean(avg_speed[c][corner])
        elevation_change[c][corner] = np.mean(elevation_change[c][corner])

speed = []
el = []

for _, d in circuit.iterrows():
    speed.append(avg_speed[d['Track']][d['Corner Number']])
    el.append(elevation_change[d['Track']][d['Corner Number']])

circuit['Avg Speed'] = speed
circuit['Elevation Change'] = el
circuit.to_csv('./circuit_info_final.csv', index=False)
                