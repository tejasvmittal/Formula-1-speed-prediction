import pandas as pd  
import numpy as np


telemetry = pd.read_csv('./telemetry.csv')


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

telemetry['Radius of Curvature'] = calculate_rolling_radius_of_curvature()
telemetry['Radius of Curvature'] = telemetry['Radius of Curvature'].ffill()
telemetry.to_csv('./telemetry_roc.csv')