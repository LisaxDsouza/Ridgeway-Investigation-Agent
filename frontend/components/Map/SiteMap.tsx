'use client';

import React, { useEffect, useRef } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { useIncidentStore } from '@/lib/store';

export default function SiteMap() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const { incidents, selectedIncidentId, selectIncident } = useIncidentStore();

  useEffect(() => {
    if (map.current || !mapContainer.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: 'https://demotiles.maplibre.org/style.json', // Standard light style
      center: [28.185, -25.864], // Ridgeway Block C
      zoom: 15,
    });

    map.current.addControl(new maplibregl.NavigationControl(), 'top-right');
  }, []);

  // Sync Markers
  useEffect(() => {
    if (!map.current) return;

    // Clear existing markers (Basic implementation for MVP)
    // In production, use GeoJSON source/layers for better performance
    
    incidents.forEach((incident) => {
      const el = document.createElement('div');
      el.className = `w-6 h-6 rounded-full border-4 border-white shadow-lg cursor-pointer transition-transform hover:scale-125 ${
        selectedIncidentId === incident.id ? 'bg-skylark-orange z-10 scale-125' : 'bg-slate-400'
      }`;
      
      el.addEventListener('click', () => {
        selectIncident(incident.id);
        map.current?.flyTo({
          center: [incident.cluster_center_lon, incident.cluster_center_lat],
          zoom: 17,
          essential: true
        });
      });

      new maplibregl.Marker({ element: el })
        .setLngLat([incident.cluster_center_lon, incident.cluster_center_lat])
        .addTo(map.current!);
    });
  }, [incidents, selectedIncidentId]);

  return (
    <div className="relative w-full h-full rounded-2xl overflow-hidden shadow-sm border border-slate-100">
      <div ref={mapContainer} className="w-full h-full" />
      
      {/* Map Overlay: Site Controls */}
      <div className="absolute top-4 left-4 flex flex-col gap-2">
        <div className="bg-white/90 backdrop-blur-md p-3 rounded-xl border border-white shadow-xl">
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">Site Perimeter</p>
          <p className="text-sm font-bold text-slate-800">Ridgeway Sector 7</p>
        </div>
      </div>
    </div>
  );
}
