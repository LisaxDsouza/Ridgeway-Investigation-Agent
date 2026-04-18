import numpy as np
from sklearn.cluster import DBSCAN
from typing import List, Dict

def cluster_events_by_location(events: List[Dict], epsilon: float = 0.002, min_samples: int = 1):
    """
    DBSCAN cluster assignments: list of clusters with member event IDs.
    epsilon = 0.002 is roughly 200m in lat/lon coordinates.
    """
    if not events:
        return []

    # Extract coordinates
    coords = np.array([[e['lat'], e['lon']] for e in events])
    
    # Run DBSCAN
    clustering = DBSCAN(eps=epsilon, min_samples=min_samples).fit(coords)
    labels = clustering.labels_
    
    # Group events by cluster label
    clusters = {}
    for i, label in enumerate(labels):
        label_key = int(label)
        if label_key not in clusters:
            clusters[label_key] = []
        clusters[label_key].append(events[i])
    
    # Return list of clusters (ignore label -1 if it was noise, though min_samples=1 prevents it)
    return list(clusters.values())
