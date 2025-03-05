import pandas as pd
import numpy as np
from collections import defaultdict
import pickle

# create segments for every track between the corner start and end distances
# create 3 features: Elevation change, Avg speed, length
# also note the start and end distance for each segment

circuit = pd.read_csv('./circuit_info_with_cluster.csv')
telemetry = pd.read_csv('./new_telemetry.csv')
track_length = pd.read_csv('./F1/data/track_data.csv')
telemetry.reset_index(drop=True)

circuits = ['Abu Dhabi', 'Australia', 'Austria', 'Azerbaijan', 'Bahrain', 'Belgium',
 'Brazil', 'Canada', 'Emilia Romagna', 'France', 'Great Britain', 'Hungary',
 'Italy', 'Japan', 'Mexico', 'Miami', 'Monaco', 'Netherlands', 'Saudi Arabia',
 'Singapore', 'Spain', 'United States', 'Las Vegas', 'China']

years = [2022, 2023, 2024]
teams = ['Red Bull Racing', 'Mercedes', 'McLaren', 'Ferrari', 'Aston Martin', 'Haas F1 Team', 'Alpine', 'Williams', 'Kick Sauber', 'RB']


def get_start_end_distance():
    start_end_distances = defaultdict(lambda: defaultdict()) # {track: {section: [start, end] }}
    for c in circuits:
        circuit_filtered = circuit[circuit['Track'] == c]
        count = 1
        for i in range(len(circuit_filtered)-1):
            if count == 1:
                # first section
                start_end_distances[c][count] = [0, circuit_filtered.iloc[i]['Start Distance']]
            else:
                start_end_distances[c][count] = [circuit_filtered.iloc[i]['End Distance'], circuit_filtered.iloc[i+1]['Start Distance']]
            count += 1
        # add the last one seperately
        start_end_distances[c][count] = [circuit_filtered.iloc[-1]['End Distance'], track_length[track_length['Track'] == c]['Length'].iloc[0]]
    return start_end_distances


def get_avg_speed_and_elev_change():
    avg_speed = defaultdict(lambda: defaultdict(list)) # {track : {section : [speeds]}}
    elevation_change = defaultdict(lambda: defaultdict(list)) # {track : {section : [elevation change]}}
    start_end_distance = get_start_end_distance()
    for y in years:
        for team in teams:
            for c in circuits:
                for t in start_end_distance[c]:
                    s, e = start_end_distance[c][t]
                    df_positions = telemetry[(telemetry['Track'] == c) & (telemetry['Team'] == team) & (telemetry['Year'] == y) & (telemetry['Distance'] >= s) & (telemetry['Distance'] <= e)]

                    if df_positions.empty:
                        continue
                    
                    for i in range(len(df_positions)):
                        avg_speed[c][t].append(df_positions.iloc[i]['Speed'])
                    elevation_change[c][t].append(df_positions.iloc[len(df_positions)-1]['Z'] - df_positions.iloc[0]['Z'])
    for c in avg_speed:
        for section in avg_speed[c]:
            avg_speed[c][section] = np.mean(avg_speed[c][section])
            elevation_change[c][section] = np.mean(elevation_change[c][section])
    return dict(start_end_distance), dict(avg_speed), dict(elevation_change)


def build():
    df = pd.DataFrame()
    start_end_distance, avg_speed, elevation_change = get_avg_speed_and_elev_change()
    with open('start_end_distance.pkl', 'rb') as f:
        start_end_distance = pickle.load(f)
        pickle.dump(start_end_distance, f)
    with open('avg_speed.pkl', 'rb') as f:
        # pickle.dump(avg_speed, f)
        avg_speed = pickle.load(f)
    with open('elevation_change.pkl', 'rb') as f:
        # pickle.dump(elevation_change, f)
        elevation_change = pickle.load(f)
    start = []
    end = []
    track = []
    sector = []
    speed = []
    elevation = []
    for t in start_end_distance:
        for s in start_end_distance[t]:
            st, en = start_end_distance[t][s]
            start.append(st)
            end.append(en)
            track.append(t)
            sector.append(s)
            if s in avg_speed[t]:
                speed.append(avg_speed[t][s])
                elevation.append(elevation_change[t][s])
            else:
                speed.append(0)
                elevation.append(0)
    df['Sector Number'] = sector
    df['Track'] = track
    df['Start Distance'] = start
    df['End Distance'] = end
    df['Average Speed'] = speed
    df['Elevation Change'] = elevation
    return df
    
build().to_csv('./power_limited_sections.csv', index=False)


