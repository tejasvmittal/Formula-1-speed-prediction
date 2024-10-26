import pandas as pd
import numpy as np

df = pd.read_csv('./data/best_quali_telemetry(2022-2024).csv')


# Set the time as the index
df.set_index('Time', inplace=True)

# Define the new uniform time interval (e.g., every 0.1 seconds)
uniform_time_index = np.arange(df.index.min(), df.index.max(), step=0.1)

# Resample and interpolate the data to make the time intervals uniform
df_uniform = df.reindex(uniform_time_index).interpolate(method='linear')

# Reset the index so 'Time' becomes a column again
df_uniform.reset_index(inplace=True)
df_uniform.rename(columns={'index': 'Time'}, inplace=True)

# Display the resampled and interpolated data
df_uniform.to_csv('./data/interpolated_telemetry.csv', index=False)
