"""
First remove all entries in telemetry whose time difference is less than 0.1s.
"""


import pandas as pd
import numpy as np
import os

current_dir = os.path.dirname(__file__)
csv_path = os.path.join(current_dir, 'data', 'best_quali_telemetry(2022-2024).csv')

df = pd.read_csv('./telemetry.csv')
df_interpolated = pd.DataFrame()
print(df['Track'].unique())

teams = ['Mercedes', 'Aston Martin', 'Ferrari', 'Haas F1 Team', 'Red Bull Racing', 'RB', 'Williams', 'Kick Sauber', 'McLaren', 'Alpine']
tracks = {2022:['Bahrain', 'Saudi Arabia', 'Australia', 'Emilia Romagna', 'Miami', 'Spain', 'Monaco', 'Azerbaijan', 'Canada', 'Great Britain', 'Austria', 'France', 'Hungary', 'Belgium', 'Netherlands', 'Italy', 'Singapore', 'Japan', 'United States', 'Mexico', 'Brazil', 'Abu Dhabi'],
           2023:['Bahrain', 'Saudi Arabia', 'Australia', 'Miami', 'Spain', 'Monaco', 'Canada', 'Great Britain', 'Hungary', 'Netherlands', 'Italy', 'Singapore', 'Japan', 'United States', 'Mexico', 'Las Vegas', 'Abu Dhabi'],
           2024:['Bahrain', 'Saudi Arabia', 'Australia', 'Japan', 'China', 'Miami', 'Emilia Romagna', 'Monaco', 'Canada', 'Spain', 'Austria', 'Great Britain', 'Hungary', 'Belgium', 'Netherlands', 'Italy', 'Azerbaijan', 'Singapore']
           }

for year in [2022, 2023, 2024]:
    for track in tracks[year]:
        for team in teams:
            print(year, track, team)
            df_filtered = df[(df['Year'] == year) & (df['Team'] == team) & (df['Track'] == track)]
            # Set the time as the index
            df_filtered.set_index('Time', inplace=True)
            if len(df_filtered.index) == 0:
                continue

            # Define the new uniform time interval (e.g., every 0.1 seconds)
            uniform_time_index = np.arange(df_filtered.index.min(), df_filtered.index.max(), step=0.1)

            # Resample and interpolate the data to make the time intervals uniform
            df_uniform = df_filtered.reindex(uniform_time_index)

            cols_to_interpolate = ['DistanceToDriverAhead', 'RPM', 'Speed', 'Distance', 'RelativeDistance', 'X', 'Y', 'Time Difference']
            df_uniform[cols_to_interpolate] = df_uniform[cols_to_interpolate].interpolate(method='linear')
            
            for col in df_uniform.columns.difference(cols_to_interpolate):
                df_uniform[col] = df_uniform[col].ffill()


            # Reset the index so 'Time' becomes a column again
            df_uniform.reset_index(inplace=True)
            df_uniform.rename(columns={'index': 'Time'}, inplace=True)
            threshold = 0.01  # Define an acceptable minimal change threshold
            df_uniform = df_uniform.loc[(df_uniform[cols_to_interpolate].diff().abs() > threshold).any(axis=1)]

            df_interpolated = pd.concat([df_interpolated, df_uniform])
# Display the resampled and interpolated data
# df_interpolated.to_csv('./interpolated_telemetry.csv', index=False)
