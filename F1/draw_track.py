import matplotlib as mpl
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from limited_sections_copy import get_sectors

colormap = mpl.cm.plasma

data = pd.read_csv('./data/best_quali_telemetry(2022-2024).csv')
data = data[(data['Track'] == 'Netherlands') & (data['Year'] == 2023)]
res = pd.read_csv('./data/power_grip_limited_sections.csv')
sectors = get_sectors(data)[0]['Netherlands']
# print(sectors)
res = res[(res['Track'] == 'Netherlands') & (res['Year'] == 2024)]


# Get telemetry data
x = np.array(data[(data['Track'] == 'Netherlands') & (data['Team'] == 'Red Bull Racing') & (data['Year'] == 2023)]['X'])
y = np.array(data[(data['Track'] == 'Netherlands') & (data['Team'] == 'Red Bull Racing') & (data['Year'] == 2023)]['Y'])
distances = np.array(data[(data['Track'] == 'Netherlands') & (data['Team'] == 'Red Bull Racing') & (data['Year'] == 2023)]['Distance'])

# sector_x = []
# sector_y = []
teams = ['Red Bull Racing', 'Aston Martin', 'Haas F1 Team', 'Williams', 'Alpine', 'McLaren', 'Ferrari', 'Mercedes', 'RB', 'Kick Sauber']

for team in teams:
    team_res = res[res['Team'] == team]
    color = []
    for i in range(len(distances)):
        for s in sectors:
            if sectors[s][0] <= distances[i] <= sectors[s][1]:
                color.append(res[res['Sector'] == s]['Speed'])
                break

    color = np.array(color).T.flatten()
    print(color)      
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    fig, ax = plt.subplots(sharex=True, sharey=True, figsize=(12, 6.75))

    # Adjust margins and turn of axis
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.12)
    ax.axis('off')


    # After this, we plot the data itself.
    # Create background track line
    ax.plot(x, y,
            color='black', linestyle='-', linewidth=16, zorder=0)

    # Create a continuous norm to map from data points to colors
    norm = plt.Normalize(color.min(), color.max())
    lc = LineCollection(segments, cmap=colormap, norm=norm,
                        linestyle='-', linewidth=5)

    # Set the values used for colormapping
    lc.set_array(color)

    # Merge all line segments together
    line = ax.add_collection(lc)


    # Finally, we create a color bar as a legend.
    cbaxes = fig.add_axes([0.25, 0.05, 0.5, 0.05])
    normlegend = mpl.colors.Normalize(vmin=color.min(), vmax=color.max())
    legend = mpl.colorbar.ColorbarBase(cbaxes, norm=normlegend, cmap=colormap,
                                    orientation="horizontal")

    plt.title('Dutch GP 2024 Speed Prediction ' + team)
    # Show the plot
    plt.savefig('dutch 2024 predictions (speed map by teams)/'+team+'.png')