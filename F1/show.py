import pandas as pd
import matplotlib.pyplot as plt

# Sample DataFrame
data = pd.read_csv('./data/power_grip_limited_sections2.csv')

df = pd.DataFrame(data)

# Separate data by Rating
grip_limited = df[df['Rating'] == 'G']['Radius of Curvature']
power_limited = df[df['Rating'] == 'P']['Radius of Curvature']

# Plot histogram
plt.figure(figsize=(8,6))
plt.hist(grip_limited, bins=10, alpha=0.5, label='Grip Limited (G)', color='blue')
plt.hist(power_limited, bins=10, alpha=0.5, label='Power Limited (P)', color='orange')

# Add labels and title
plt.xlabel('Radius of Curvature')
plt.ylabel('Frequency')
plt.title('Comparison of Radius of Curvature for G and P')
plt.legend(loc='upper right')

# Show plot
plt.show()
