from ...tools.spatial_tools import cluster_events_by_location

async def handle(events):
    try:
        if not events:
            return {"cluster_count": 0, "clusters": []}
            
        clusters = cluster_events_by_location(events)
        
        # Format the output for the agent
        formatted_clusters = []
        for i, cluster in enumerate(clusters):
            # Calculate centroid
            lats = [e['lat'] for e in cluster if 'lat' in e and e['lat'] is not None]
            lons = [e['lon'] for e in cluster if 'lon' in e and e['lon'] is not None]
            
            centroid_lat = sum(lats) / len(lats) if lats else 0
            centroid_lon = sum(lons) / len(lons) if lons else 0
            
            # Count distinct sources
            sources = set(e.get('type') or e.get('source') for e in cluster)
            
            formatted_clusters.append({
                "cluster_id": i,
                "centroid_lat": centroid_lat,
                "centroid_lon": centroid_lon,
                "event_count": len(cluster),
                "source_diversity": len(sources),
                "events": cluster
            })
            
        return {
            "cluster_count": len(formatted_clusters),
            "clusters": formatted_clusters
        }
    except Exception as e:
        return {"cluster_count": 0, "error": str(e)}
