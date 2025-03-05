import pandas as pd  
import numpy as np
from collections import defaultdict

circuit = pd.read_csv('./circuit_info_with_end_dist.csv')
telemetry = pd.read_csv('./telemetry.csv')

circuits = ['Abu Dhabi', 'Australia', 'Austria', 'Azerbaijan', 'Bahrain', 'Belgium',
 'Brazil', 'Canada', 'Emilia Romagna', 'France', 'Great Britain', 'Hungary',
 'Italy', 'Japan', 'Mexico', 'Miami', 'Monaco', 'Netherlands', 'Saudi Arabia',
 'Singapore', 'Spain', 'United States', 'Las Vegas', 'China']

years = [2022, 2023, 2024]
teams = ['Red Bull Racing', 'Mercedes', 'McLaren', 'Ferrari', 'Aston Martin', 'Haas F1 Team', 'Alpine', 'Williams', 'Kick Sauber', 'RB']

angle_change = defaultdict(lambda: defaultdict(list))

def calculate_total_angle_change(telemetry, start_dist, end_dist):
    # Filter data within the corner distance range
    corner_data = telemetry[(telemetry['Distance'] >= start_dist) & 
                            (telemetry['Distance'] <= end_dist)]    
    # Calculate heading angles
    angles = np.arctan2(corner_data['Y'].diff(), corner_data['X'].diff())    
    # Calculate angle changes between consecutive points
    angle_changes = angles.diff().fillna(0)    
    # Normalize angle changes to handle wraparound
    angle_changes = (angle_changes + np.pi) % (2 * np.pi) - np.pi  
    # angle_changes = np.unwrap(angle_changes)  
    # Calculate total angle change as sum of absolute angle changes
    total_angle_change = np.abs(angle_changes).sum()
    total_angle_change_degrees = total_angle_change * (180 / np.pi)
    print(total_angle_change_degrees)
    return total_angle_change_degrees

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
                corner_info = df_corners[df_corners['Corner Number'] == corner_num].iloc[0]
                angle_change[c][corner_num].append(calculate_total_angle_change(df_positions, corner_info['Start Distance'], corner_info['End Distance']))

print(angle_change)

for c in angle_change:
    for corner_num in angle_change[c]:
        angle_change[c][corner_num] = np.mean(angle_change[c][corner_num])

ang = []
for _, data in circuit.iterrows():
    ang.append(angle_change[data['Track']][data['Corner Number']])

circuit['Angle Change'] = ang
circuit.to_csv('./circuit_info_with_angle.csv', index=False)
