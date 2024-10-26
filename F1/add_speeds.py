import pandas as pd
import matplotlib.pyplot as plt 
import numpy as np

data = pd.read_csv('./fastest_laps.csv')

track_turns = {'Bahrain', 'Saudi Arabia', 'Australia', 'Emilia Romagna', 'Miami', 'Spain', 'Monaco', 'Azerbaijan', 'Canada', 'Great Britain', 'Austria', 'Hungary', 'Belgium', 'Netherlands', 'Italy', 'Singapore', 'Japan', 'United States', 'Mexico', 'Brazil', 'Las Vegas', 'Abu Dhabi', 'France'}

def convert_laptime(laptime):
    time = laptime.split(' ')[2]
    time_list = time.split(':')
    hour = time_list[0]
    minute = time_list[1]
    sec = time_list[2]
    return float(hour) + (float(minute) / 60) + (float(sec)/(60*60))

def filter_best():
    record = {2022:{}, 2023:{}, 2024:{}}
    for _, d in data.iterrows():
        if d['Track'] not in record[d['Year']]:
            record[d['Year']][d['Track']] = {}
        if d['Team'] not in record[d['Year']][d['Track']]:
            record[d['Year']][d['Track']][d['Team']] = d
        if convert_laptime(d['LapTime']) < convert_laptime(record[d['Year']][d['Track']][d['Team']]['LapTime']):
            record[d['Year']][d['Track']][d['Team']] = d
    return record 

def get_avg_speed():
    speed = []
    for _, d in data.iterrows():
        speed.append(float(d['Track Length'])/convert_laptime(d['LapTime']))
    return speed 

if __name__ == '__main__':
    # time to plot
    avg_speed = get_avg_speed()
    data['Mean Speed'] = avg_speed
    data.to_csv('./fastest_laps.csv', index=False)


    # for _, d in data.iterrows():
    #     if d['Team'] not in record:
    #         record[d['Team']] = [[], []] # top speed, mean speed
    #     record[d['Team']][0].append(d['SpeedST'])
    #     record[d['Team']][1].append(d['Mean Speed'])
    # x = []
    # y = []
    # labels = []
    # for r in record:
    #     x.append(np.mean(record[r][1]))
    #     y.append(np.mean(record[r][0]))
    #     labels.append(r)
    # plt.scatter(x, y)
    # for i in range(len(x)):
    #     plt.annotate(labels[i], (x[i], y[i]))
    # plt.title("2024 Season Efficiency Graph")
    # plt.xlabel("Mean Speed (KMH)")
    # plt.ylabel("Top Speed (KMH)")
    # plt.show()

        
