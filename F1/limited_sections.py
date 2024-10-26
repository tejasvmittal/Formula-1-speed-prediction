import pandas as pd 
import csv
from collections import defaultdict 
import json
import numpy as np

telemetry = pd.read_csv('./data/best_quali_telemetry(2022-2024).csv')
# data = pd.read_csv('./data/power_grip_limited_sections.csv')
track_data = pd.read_csv('./data/track_data.csv')

#Power Limited sections  basically all 100% throttle areas  (throttle = 100%)
# Grip limited sections (Brake % to when they go to 100% throttle)
# -Slow section <150 kph
# -Medium sections 150kph<x<225 kph
# -Fast section >225 kph

# Baku: Rear Limited -> yes

# Barcelona: slightly Front Limited -> normally front left limited, in hot races rear thermal limitaiton

# Monaco: Rear Limited -> yes

# Montreal: Rear Limited  -> yes (new tharmac likely to shift it to the FA)

# Le Castellet: Front Limited-> yes

# Spielberg: Rear Limited -> yes

# Silverstone: slightly Front Limited -> yes

# Hockenheim: slightly Rear Limited -> no idea anymore – like absolutely no idea anymore

# Budapest: slightly Rear Limited -> In “normal” conditions thermal limitation from rear axle

# Spa: Front Limited -> yes

# Monza: Both -> rather rear

# Singapour: Rear Limited -> yes

# Sotchi: Front Limited -> yes

# Suzuka: Front Limited -> generally yes, hot track temps like this year though is rear limited

# Mexiko: Rear Limited -> both axles possible (depending on car setup and driving can be either FA or RA – wherever graining gets triggered first)

# Austin: Front Limited -> Yes

# Sao Paulo: Front Limited -> actually more rear limited in both cases (thermal and wear)

# Abu Dhabi: Rear Limited -> with latest circuit FR limitation graining
def convert_telemetry_time():
    conversion = []
    for _, d in telemetry.iterrows():
        print(d['Time'])
        if isinstance(d['Time'], str):
            m, s = d['Time'].split(' ')[-1].split(':')[1:]# t = 00:01.22112
        else:
            conversion.append(0)
            continue
        t = int(m)*60 + float(s)
        conversion.append(t)
    telemetry['Time'] = conversion


def add_speed_rating(data):
    """
    Use this after calculating every other column. Looks at the average speed of each sector to give it a rating
    """
    res = []
    for _, d in data.iterrows():
        if d['Speed'] < 150:
            res.append('S')
        elif 150 <= d['Speed'] <= 225:
            res.append('M')
        else:
            res.append('F')
    return res


def add_track_features(data):
    """
    Add all 8 track features listed by Pirelli to the dataset
    """
    traction = []
    braking = []
    lateral = []
    tyre_stress = []
    track_evo = []
    asphalt_grip = []
    asphalt_abr = []
    downforce = []
    for _, d in data.iterrows():
        track = d['Track']
        year = d['Year']
        for _, t in track_data.iterrows():
            if track == t['Track'] and year == t['Year']:
                traction.append(t['Traction'])
                braking.append(t['Braking'])
                lateral.append(t['Lateral'])
                tyre_stress.append(t['Tyre Stress'])
                track_evo.append(t['Track Evolution'])
                asphalt_grip.append(t['Asphalt Grip'])
                asphalt_abr.append(t['Asphalt Abrasion'])
                downforce.append(t['Downforce'])
                break
    return traction, braking, lateral, tyre_stress, track_evo, asphalt_grip, asphalt_abr, downforce


def get_sectors():
    """ 
    Looks at the telemetry data 
    """    
    sectors = {} # {track : {sector no. : [start distance, end distance, Power/Grip]}}
    sectors_years = [] # [sectors]
    start = 0
    end = 0
    rating = 'P'
    sector_count = 0
    current_track = ""
    current_year = 2022
    team = ""

    for i, d in telemetry.iterrows():
        if current_year != d['Year']:
            sectors_years.append(sectors)
            sectors = {}
            current_year = d['Year']

        if current_track != d['Track']:
            start = d['Distance']
            rating = 'P'
            sectors[d['Track']] = {}
            current_track = d['Track']
            team = d['Team']
        
        if team != d['Team'] and sector_count != 0:
            end = telemetry.loc[i-1]['Distance']
            sectors[d['Track']][sector_count] = [start, end, rating]
            rating = ''
            start = 0
            end = 0
            sector_count = 0
            continue

        if rating == 'G' and d['Throttle'] == 100:
            # start of power limit sector
            end = d['Distance']
            sectors[d['Track']][sector_count] = [start, end, rating]
            rating = 'P'
            start = end
            end = 0
            sector_count += 1
        
        if rating == 'P' and d['Throttle'] != 100:
            # start of grip limit sector
            end = d['Distance']
            sectors[d['Track']][sector_count] = [start, end, rating]
            rating = 'G'
            start = end
            end = 0
            sector_count += 1
    sectors_years.append(sectors)
    return sectors_years


def create_dataset():
    """
    Returns the main power/grip limited section dataset from the telemetry, call every function that depends on power/grip dataset after this.
    Call this function after adding radius of curvature to telemetry data
    """
    sectors = get_sectors()
    df = {} # {year: {track: {sector: {team: [speed, rating, radius of curvature]}}}}}
    year = 2021
    for y in range(3):
        year += 1
        df[year] = {}
        for track in sectors[y]:
            df[year][track] = {}
            for sector in sectors[y][track]:
                df[year][track][sector] = {}
                start = sectors[y][track][sector][0]
                end = sectors[y][track][sector][1]
                rating = sectors[y][track][sector][2]
                filtered_df = telemetry[(telemetry['Year'] == year) & (telemetry['Track'] == track)]
                speeds = []
                roc = []
                current_team = ''

                for _, d in filtered_df.iterrows():
                    if d['Team'] != current_team:
                        print(current_team, speeds)
                        avg_speed = np.mean(speeds) if speeds != [] else 0
                        avg_roc = np.mean(roc) if roc != [] else 0
                        df[year][track][sector][current_team] = [avg_speed, avg_roc, rating]
                        current_team = d['Team']
                        speeds = []  
                        roc = []

                    point = d['Distance']
                    if start <= point <= end:
                        speeds.append(d['Speed'])
                        roc.append(d['Radius of Curvature'])
                print(current_team, speeds, roc)
                avg_speed = np.mean(speeds) if speeds != [] else 0
                avg_roc = np.mean(roc) if roc != [] else 0
                df[year][track][sector][current_team] = [avg_speed, avg_roc, rating]
    return df

def flatten_dict(d, parent_keys=[]):
    items = []
    for k, v in d.items():
        new_keys = parent_keys + [k]
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_keys))
        else:
            items.append((*new_keys, *v))
    return items


def calculate_rolling_radius_of_curvature(window_size=3):
    """
    Calculate the radius of curvature on a rolling basis for each sample.
    for each track and each year do only once, pick any team to do it for
    """

    radius_of_curvature = []
    j=0
    n = len(telemetry)
    while j<n:
        current_year = telemetry.loc[j, 'Year']
        current_track = telemetry.loc[j, 'Track']
        filtered_df = telemetry[(telemetry['Year'] == current_year) & (telemetry['Track'] == current_track)]
        m = len(filtered_df)
        for i in range(m):
            j+=1
            # Define the window of points around the current point
            start = max(0, i - window_size)
            end = min(m, i + window_size)

            if end - start < 3:  # Need at least three points to calculate curvature
                radius_of_curvature.append(np.nan)  # Not enough points
                continue

            # Extract the windowed X and Y coordinates
            X_window = list(filtered_df.iloc[start:end, telemetry.columns.get_loc('X')])
            Y_window = list(filtered_df.iloc[start:end, telemetry.columns.get_loc('Y')])
            time_window = list(filtered_df.iloc[start:end, telemetry.columns.get_loc('Time')])
            # Calculate the time difference (dt) for the window
            dt = (time_window[-1] - time_window[0]) / (end - start - 1)

            # Calculate velocity components
            v_x = (X_window[-1] - X_window[0]) / ((end - start - 1) * dt)
            v_y = (Y_window[-1] - Y_window[0]) / ((end - start - 1) * dt)

            # Calculate acceleration components (using central differences)
            a_x = (X_window[-1] - 2 * X_window[-2] + X_window[-3]) / (dt ** 2)
            a_y = (Y_window[-1] - 2 * Y_window[-2] + Y_window[-3]) / (dt ** 2)

            # Calculate radius of curvature
            denominator = v_x * a_y - v_y * a_x
            if denominator != 0:  # Avoid division by zero
                r = ((v_x**2 + v_y**2)**(3/2)) / abs(denominator)
                radius_of_curvature.append(r)
            else:
                radius_of_curvature.append(np.nan)  # Division by zero

    return radius_of_curvature



if __name__ == '__main__':

    flattened_data = flatten_dict(create_dataset())
    columns = ['Year', 'Track', 'Sector', 'Team', 'Speed', 'Rating', 'Radius of Curvature']
    df = pd.DataFrame(flattened_data, columns=columns)
    traction, braking, lateral, tyre_stress, track_evo, asphalt_grip, asphalt_abr, downforce = add_track_features(df)
    speed_rating = add_speed_rating(df)
    df['Speed Rating'] = speed_rating
    df['Traction'] = traction
    df['Braking'] = braking
    df['Lateral'] = lateral
    df['Tyre Stress'] = tyre_stress
    df['Track Evolution'] = track_evo
    df['Asphalt Grip'] = asphalt_grip
    df['Asphalt Abrasion'] = asphalt_abr
    df['Downforce'] = downforce
    df.to_csv('./data/power_grip_limited_sections2.csv', index=False)
    # x = get_rear_front_limit_classification()
    # print(x)
    # with open('./output.json', 'w') as file:
    #     json.dump(df, file, indent=4)

