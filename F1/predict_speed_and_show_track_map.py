import pandas as pd  
import numpy as np
from collections import defaultdict
from matplotlib import pyplot as plt
from adjustText import adjust_text

TRACK = 'Las Vegas'
YEAR = 2024
TEAMS = ['Williams', 'RB', 'Kick Sauber']

circuit = pd.read_csv('./circuit_info_with_cluster.csv')
telemetry = pd.read_csv('./new_telemetry.csv')


def get_cluster_speed(track, year, teams):
    clusters = circuit[circuit['Track'] == track]['Cluster']
    tel = telemetry[telemetry['Year'] == year]

    cluster_speeds = defaultdict(lambda: defaultdict(list)) # {cluster number :{team : [speed]}}

    for team in teams:
        for c in clusters:
            circuit_filtered = circuit[circuit['Cluster'] == c]
            for _, corner in circuit_filtered.iterrows():
                start = corner['Start Distance']
                end = corner['End Distance']
                track = corner['Track']
                telemetry_filtered = tel[(tel['Distance'] >= start) & (tel['Distance'] <= end) & (tel['Track'] == track) & (tel['Team'] == team)]
                
                if telemetry_filtered.empty:
                    continue                
                for _, t in telemetry_filtered.iterrows():
                    cluster_speeds[c][team].append(t['Speed'])
    
    for c in cluster_speeds:
        for t in cluster_speeds[c]:
            cluster_speeds[c][t] = np.mean(cluster_speeds[c][t])    
    return cluster_speeds



def rotate(xy, *, angle):
    rot_mat = np.array([[np.cos(angle), np.sin(angle)],
                        [-np.sin(angle), np.cos(angle)]])
    return np.matmul(xy, rot_mat)



def draw_track_map1(track, year, teams):
    cluster_speed = get_cluster_speed(track, year, teams)
    telemetry_filtered = telemetry[(telemetry['Team'] == 'Red Bull Racing') & (telemetry['Year'] == 2023) & (telemetry['Track'] == track)] 
    circuit_filered = circuit[circuit['Track'] == track]
    x = telemetry_filtered['X']
    y = telemetry_filtered['Y']
    for team in teams:
        colors = []
        offset = 0
        prev = 0
        for _, t in telemetry_filtered.iterrows():
            distance = t['Distance']
            for _, c in circuit_filered.iterrows():
                start = c['Start Distance']
                end = c['End Distance']
                if start <= distance <= end:
                    colors.append(cluster_speed[c['Cluster']][team])
                    break
            if prev == len(colors):
                colors.append(0)
            prev = len(colors) 


        # implement here   
        track = telemetry_filtered.loc[:, ('X', 'Y')].to_numpy()
        track_angle = circuit_filered['Angle'] / 180 * np.pi
        rotated_track = rotate(track, angle=track_angle)
        
        # Create plot
        fig, ax = plt.subplots()
        ax.plot(rotated_track[:, 0], rotated_track[:, 1])


        # Create a continuous norm to map from data points to colors
   
        offset += 100
    plt.show()  


def draw_track_map2(track, year, teams):
    cluster_speed = get_cluster_speed(track, year, teams)
    telemetry_filtered = telemetry[(telemetry['Team'] == 'Red Bull Racing') & (telemetry['Year'] == 2023) & (telemetry['Track'] == track)] 
    circuit_filtered = circuit[circuit['Track'] == track]
    track = telemetry_filtered.loc[:, ('X', 'Y')].to_numpy()
    track_angle = 90.0 / 180 * np.pi
    rotated_track = rotate(track, angle=track_angle)
    plt.plot(rotated_track[:, 0], rotated_track[:, 1])
    offset_vector = [500, 0]
    texts = []
    for _, corner in circuit_filtered.iterrows():
    # Create a string from corner number and letter
        txt = f"{corner['Number']}-KS:{cluster_speed[corner['Cluster']]['Kick Sauber']:.1f}, RB:{cluster_speed[corner['Cluster']]['RB']:.1f}, WL:{cluster_speed[corner['Cluster']]['Williams']:.1f}"
        # Convert the angle from degrees to radian.
        offset_angle = corner['Angle'] / 180 * np.pi

        # Rotate the offset vector so that it points sideways from the track.
        offset_x, offset_y = rotate(offset_vector, angle=offset_angle)

        # Add the offset to the position of the corner
        text_x = corner['X'] + offset_x
        text_y = corner['Y'] + offset_y

        # Rotate the text position equivalently to the rest of the track map
        text_x, text_y = rotate([text_x, text_y], angle=track_angle)

        # Rotate the center of the corner equivalently to the rest of the track map
        track_x, track_y = rotate([corner['X'], corner['Y']], angle=track_angle)

        # Draw a circle next to the track.
        # plt.scatter(text_x, text_y, color='grey', s=140)

        # Draw a line from the track to this circle.
        plt.plot([track_x, text_x-1], [track_y, text_y-1], color='gray')

        # Finally, print the corner number inside the circle.
        txt = plt.text(text_x, text_y, txt,
                va='center_baseline', ha='center', size='small', color='black')
        texts.append(txt)
    adjust_text(texts, arrowprops=dict(arrowstyle='-', color='grey', lw=0.5))
    plt.axis('off')
    plt.show()

draw_track_map2(TRACK, YEAR, TEAMS)







