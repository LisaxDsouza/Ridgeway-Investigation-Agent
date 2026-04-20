'use client';

import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useIncidentStore } from '@/lib/store';
import { Shield, AlertTriangle, Info, Map as MapIcon, Layers, Radio } from 'lucide-react';
import { clsx } from 'clsx';

// Fix for default marker icons in Next.js/React-Leaflet
const DefaultIcon = L.icon({
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
});
L.Marker.prototype.options.icon = DefaultIcon;

const SensorIcon = L.divIcon({
  className: 'custom-div-icon',
  html: "<div style='background-color:#f05b28; width:12px; height:12px; border-radius:50%; border:2px solid white; box-shadow: 0 0 10px rgba(240,91,40,0.5);'></div>",
  iconSize: [12, 12],
  iconAnchor: [6, 6]
});

const AccessIcon = L.divIcon({
  className: 'custom-div-icon',
  html: "<div style='background-color:#2e3a59; width:12px; height:12px; border-radius:50%; border:2px solid white; box-shadow: 0 0 10px rgba(46,58,89,0.5);'></div>",
  iconSize: [12, 12],
  iconAnchor: [6, 6]
});

export default function SituationMap() {
  const { unifiedEvents, fetchEvents, isLoading } = useIncidentStore();
  const [selectedEventId, setSelectedEventId] = React.useState<string | null>(null);

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  const center: [number, number] = [13.0485, 77.5435];

  // Selected/Highlight Icon
  const HighlightIcon = L.divIcon({
    className: 'custom-div-icon',
    html: "<div style='background-color:#f05b28; width:24px; height:24px; border-radius:50%; border:4px solid white; box-shadow: 0 0 20px rgba(240,91,40,0.8);' class='animate-ping'></div>",
    iconSize: [24, 24],
    iconAnchor: [12, 12]
  });

  return (
    <div className="h-full flex flex-col bg-[#fdfdfd]">
      <div className="p-8 border-b border-slate-50 flex items-center justify-between bg-white/50 backdrop-blur-md sticky top-0 z-[1000]">
        <div className="flex items-center gap-4">
           <div className="p-3 bg-orange-100 rounded-2xl text-skylark-orange shadow-sm">
              <MapIcon className="w-6 h-6" />
           </div>
           <div>
              <h1 className="text-2xl font-extrabold text-[#2e3a59] tracking-tight">HMT Watch Factory Command</h1>
              <p className="text-sm text-slate-400 font-medium italic">Ridgeway Industry Zone • 13.0485, 77.5435</p>
           </div>
        </div>
        
        <div className="flex items-center gap-3">
           <div className="flex items-center gap-6 px-6 py-3 bg-white rounded-2xl border border-slate-100 shadow-sm">
              <div className="flex items-center gap-2">
                 <div className="w-3 h-3 rounded-full bg-skylark-orange" />
                 <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Telemetry</span>
              </div>
              <div className="flex items-center gap-2">
                 <div className="w-3 h-3 rounded-full bg-[#2e3a59]" />
                 <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Access Control</span>
              </div>
           </div>
        </div>
      </div>

      <div className="flex-1 relative">
        <MapContainer 
          center={center} 
          zoom={17} 
          dragging={false}
          zoomControl={false}
          scrollWheelZoom={false}
          touchZoom={false}
          doubleClickZoom={false}
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          
          {unifiedEvents.map((event) => (
            event.lat && event.lon && (
              <Marker 
                key={event.id} 
                position={[event.lat, event.lon]}
                icon={selectedEventId === event.id ? HighlightIcon : (event.source === 'access' ? AccessIcon : SensorIcon)}
              >
                <Popup>
                  <div className="p-2 min-w-[200px] font-sans">
                    <div className="flex items-center justify-between mb-2 pb-2 border-b border-slate-50">
                       <span className={clsx(
                         "text-[10px] font-black uppercase tracking-tighter px-2 py-0.5 rounded-full",
                         event.source === 'access' ? "bg-slate-100 text-slate-600" : "bg-orange-100 text-skylark-orange"
                       )}>
                          {event.source}
                       </span>
                       <span className="text-[10px] text-slate-300 font-bold">{new Date(event.time).toLocaleTimeString()}</span>
                    </div>
                    <p className="text-sm font-bold text-[#2e3a59] mb-1">{event.type}</p>
                    <p className="text-xs text-slate-400 font-medium italic">Zone: {event.zone}</p>
                  </div>
                </Popup>
              </Marker>
            )
          ))}
        </MapContainer>

        {/* 📋 Side Panel Overlay */}
        <div className="absolute top-8 right-8 w-80 bg-white/90 backdrop-blur-xl rounded-[2.5rem] border border-slate-100 shadow-2xl p-8 z-[1000] max-h-[calc(100%-4rem)] overflow-hidden flex flex-col">
           <div className="flex items-center gap-3 mb-6">
              <Radio className="w-5 h-5 text-skylark-orange animate-pulse" />
              <h2 className="text-lg font-extrabold text-[#2e3a59]">Live Feed</h2>
           </div>
           
           <div className="space-y-4 overflow-y-auto pr-2 scrollbar-hide">
              {unifiedEvents.slice(0, 20).map((event) => (
                <div 
                  key={event.id} 
                  onClick={() => setSelectedEventId(event.id)}
                  className={clsx(
                    "p-4 rounded-2xl cursor-pointer border transition-all group",
                    selectedEventId === event.id 
                      ? "bg-orange-50 border-skylark-orange shadow-md ring-2 ring-orange-100" 
                      : "bg-white border-slate-50 shadow-sm hover:border-orange-100"
                  )}
                >
                   <div className="flex items-center justify-between mb-1">
                      <span className={clsx(
                        "text-[9px] font-bold transition-colors",
                        selectedEventId === event.id ? "text-skylark-orange" : "text-slate-300 group-hover:text-skylark-orange"
                      )}>
                        {new Date(event.time).toLocaleTimeString()}
                      </span>
                      <div className={clsx(
                        "w-1.5 h-1.5 rounded-full",
                        event.severity === 'high' ? "bg-red-500" : "bg-skylark-orange"
                      )} />
                   </div>
                   <p className={clsx(
                     "text-xs font-bold",
                     selectedEventId === event.id ? "text-skylark-orange" : "text-[#2e3a59]"
                   )}>{event.type}</p>
                   <p className="text-[10px] text-slate-400 mt-1">{event.zone}</p>
                </div>
              ))}
              
              {unifiedEvents.length === 0 && (
                <div className="text-center py-10">
                   <p className="text-xs font-bold text-slate-300">No active signals detected in this quadrant.</p>
                </div>
              )}
           </div>
        </div>
      </div>
    </div>
  );
}
