import numpy as np
import analyze_player
from sklearn.cluster import KMeans, AffinityPropagation
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import mpld3

player_dfs = analyze_player.get_player_dfs("./player_stats/")

# Only look at the below stats. (This is currently an arbitrary choice.)
use_stats = ["k", "e", "ta", "pct", "digs"]

labels = list(player_dfs.keys())
X = [player_dfs[name][use_stats].mean().values for name in labels]
# Filter players with nans for any of these stats.
X = [row for row in X if not np.isnan(row).any()]
X = np.array(X)

pca = PCA(n_components=2)
X_pca = pca.fit(X).transform(X)

clf = KMeans(n_clusters=4)
clf.fit(X_pca)

h = .02
# Plot the decision boundary. For that, we will assign a color to each cluster.
x_min, x_max = X_pca[:, 0].min() - 1, X_pca[:, 0].max() + 1
y_min, y_max = X_pca[:, 1].min() - 1, X_pca[:, 1].max() + 1
xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

# Obtain labels for each point in mesh. Use the last trained model.
Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])

# Put the result into a color plot.
Z = Z.reshape(xx.shape)
cmap = plt.cm.Paired
plt.imshow(Z, interpolation='nearest',
           extent=(xx.min(), xx.max(), yy.min(), yy.max()),
           cmap=cmap,
           aspect='auto', origin='lower')

scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], s=30, color="k")

tooltip = mpld3.plugins.PointLabelTooltip(scatter, labels=labels)
mpld3.plugins.connect(plt.gcf(), tooltip)

# Plot the centroids as a white X
centroids = clf.cluster_centers_
plt.scatter(centroids[:, 0], centroids[:, 1],
            marker='x', s=169, linewidths=3,
            color='w', zorder=10)
plt.xlim(x_min, x_max)
plt.ylim(y_min, y_max)
plt.xticks(())
plt.yticks(())
plt.title("K-means Clustering of Oglethorpe Volleyball Players")

plt.show()
