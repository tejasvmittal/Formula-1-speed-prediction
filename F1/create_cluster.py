import pandas as pd
import numpy as np
from sklearn.manifold import TSNE
from sklearn.cluster import AgglomerativeClustering
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
from adjustText import adjust_text
TRACK = 'Las Vegas'

data = pd.read_csv("./power_limited_sections.csv")

features = data[['Avg Speed', 'Elevation Change', 'Length']]

# Apply t-SNE for dimensionality reduction to 2 dimensions
tsne = TSNE(n_components=2, random_state=0)
features_2d = tsne.fit_transform(features)

# Perform hierarchical clustering
cluster = AgglomerativeClustering(n_clusters=125)
cluster_labels = cluster.fit_predict(features_2d)

# Add the 2D features and cluster labels to the original dataframe for plotting
data['t-SNE-1'] = features_2d[:, 0]
data['t-SNE-2'] = features_2d[:, 1]
data['Cluster'] = cluster_labels

# Plot the clusters
plt.figure(figsize=(12, 8))
# scatter = plt.scatter(features_2d[:, 0], features_2d[:, 1], c=data['Cluster'], cmap='viridis', s=50)

# track_clusters = data[data['Track'] == TRACK]['Cluster'].unique()

# Plot the clusters, but only for those containing Las Vegas data

for label in np.unique(cluster_labels):
    # Only plot clusters that contain data from Las Vegas
    if label in data['Cluster']:
        # Filter points of the current cluster
        cluster_points = features_2d[cluster_labels == label]

        # Calculate cluster centroid in 2D space
        centroid = cluster_points.mean(axis=0)

        # Calculate the maximum distance from the centroid to define the circle radius
        distances = cdist(cluster_points, [centroid], metric='euclidean')
        radius = distances.max() * 1.1  # Scale up the radius a bit for a clear boundary

        # Plot the cluster points
        plt.scatter(cluster_points[:, 0], cluster_points[:, 1], s=50)
        
        # Draw a circle around each cluster
        circle = plt.Circle(centroid, radius, color='grey', fill=False, linestyle='--', linewidth=2)
        plt.gca().add_patch(circle)

# Annotate each point with its label from the original data
texts = []
for i, label in enumerate(data['Label']):
    if data['Cluster'].iloc[i] in data:
        text = plt.text(features_2d[i, 0], features_2d[i, 1], label, fontsize=8, alpha=0.7)
        texts.append(text)

# Adjust text to prevent overlap
adjust_text(texts, arrowprops=dict(arrowstyle='-', color='grey', lw=0.5))

data.to_csv('./power_limited_with_cluster.csv', index=False)
plt.title("Hierarchical Clustering of F1 Corners with t-SNE Reduction")
plt.xlabel("t-SNE Dimension 1")
plt.ylabel("t-SNE Dimension 2")
plt.legend(title='Cluster')
plt.show()
