'use client';

import React, { useEffect, useState } from 'react';
import { useIncidentStore } from '@/lib/store';
import api from '@/lib/api';
import { 
  Radio, Zap, MapPin, Clock, Search, 
  Activity, Check, ShieldAlert, Truck, Plane, Key,
  ExternalLink, ArrowRight, Database
} from 'lucide-react';
import { clsx } from 'clsx';

type RawTab = 'sensors' | 'access' | 'vehicles' | 'drones';

export default function ControlRoom() {
  const { fetchEvents, triggerScan, isScanning } = useIncidentStore();
  const [activeRawTab, setActiveRawTab] = useState<RawTab>('sensors');
  const [rawData, setRawData] = useState<any[]>([]);
  const [isIngesting, setIsIngesting] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const fetchRawData = async (tab: RawTab) => {
    setIsLoading(true);
    try {
      const response = await api.get(`/events/${tab}`);
      setRawData(response.data);
    } catch (err) {
      console.error(`Failed to fetch ${tab}`, err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRawData(activeRawTab);
  }, [activeRawTab]);

  const ingestSample = async (scenario: string) => {
    setIsIngesting(true);
    try {
      if (scenario === 'breach') {
        await api.post('/events/ingest', {
          source: 'sensor', type: 'fence_vibration', zone: 'HMT-North-Perimeter',
          lat: 13.0485, lon: 77.5435
        });
        await api.post('/events/ingest', {
          source: 'access', type: 'fail', zone: 'HMT-Staff-Gate',
          lat: 13.0486, lon: 77.5436, data: { badge_id: 'UNKNOWN-X' }
        });
      } else if (scenario === 'vehicle') {
        await api.post('/events/ingest', {
          source: 'vehicle', type: 'truck', zone: 'HMT-Loading-Dock',
          lat: 13.0487, lon: 77.5437, data: { vehicle_id: 'SUSPECT-01' }
        });
      }
      fetchRawData(activeRawTab);
      fetchEvents();
    } catch (err) {
      console.error('Ingestion failed', err);
    } finally {
      setIsIngesting(false);
    }
  };

  const renderTableHeaders = () => {
    switch (activeRawTab) {
      case 'sensors':
        return ['Result', 'Sensor Type', 'Sensor ID', 'Zone', 'Timestamp'];
      case 'access':
        return ['Result', 'Outcome', 'Badge ID', 'Gate ID', 'Timestamp'];
      case 'vehicles':
        return ['Result', 'Vehicle Type', 'Vehicle ID', 'In Restricted', 'Timestamp'];
      case 'drones':
        return ['Result', 'Mission', 'Drone ID', 'Observation', 'Timestamp'];
      default:
        return [];
    }
  };

  const renderRow = (item: any) => {
    const timeStr = new Date(item.recorded_at).toLocaleString();
    switch (activeRawTab) {
      case 'sensors':
        return (
          <>
            <td className="py-4 px-6">
              <div className={clsx("w-2 h-2 rounded-full", item.threshold_breached ? "bg-red-500" : "bg-green-500")} />
            </td>
            <td className="py-4 px-6 font-bold text-[#2e3a59]">{item.sensor_type}</td>
            <td className="py-4 px-6 text-slate-400 text-xs font-mono">{item.sensor_id}</td>
            <td className="py-4 px-6 text-slate-500 font-medium">{item.zone}</td>
            <td className="py-4 px-6 text-slate-400 text-xs">{timeStr}</td>
          </>
        );
      case 'access':
        return (
          <>
            <td className="py-4 px-6">
              <div className={clsx("w-2 h-2 rounded-full", item.outcome === 'fail' ? "bg-red-500" : "bg-green-500")} />
            </td>
            <td className="py-4 px-6 font-bold text-[#2e3a59] capitalize">{item.outcome}</td>
            <td className="py-4 px-6 text-slate-500 font-medium">{item.badge_id}</td>
            <td className="py-4 px-6 text-slate-400 text-xs">{item.gate_id}</td>
            <td className="py-4 px-6 text-slate-400 text-xs">{timeStr}</td>
          </>
        );
      case 'vehicles':
        return (
          <>
            <td className="py-4 px-6">
              <div className={clsx("w-2 h-2 rounded-full", item.in_restricted ? "bg-orange-500" : "bg-green-500")} />
            </td>
            <td className="py-4 px-6 font-bold text-[#2e3a59] capitalize">{item.vehicle_type}</td>
            <td className="py-4 px-6 text-slate-500 font-medium">{item.vehicle_id}</td>
            <td className="py-4 px-6">
               <span className={clsx("px-2 py-0.5 rounded text-[10px] font-bold uppercase", item.in_restricted ? "bg-orange-100 text-orange-600" : "bg-green-100 text-green-600")}>
                  {item.in_restricted ? 'RESTRICTED' : 'CLEAR'}
               </span>
            </td>
            <td className="py-4 px-6 text-slate-400 text-xs">{timeStr}</td>
          </>
        );
      case 'drones':
        return (
          <>
            <td className="py-4 px-6">
              <div className={clsx("w-2 h-2 rounded-full", item.flagged ? "bg-red-500" : "bg-green-500")} />
            </td>
            <td className="py-4 px-6 font-bold text-[#2e3a59]">{item.mission_id}</td>
            <td className="py-4 px-6 text-slate-500 font-medium">{item.drone_id}</td>
            <td className="py-4 px-6 text-slate-400 text-xs italic truncate max-w-[200px]">{item.observation}</td>
            <td className="py-4 px-6 text-slate-400 text-xs">{timeStr}</td>
          </>
        );
    }
  };

  const [isSeeding, setIsSeeding] = useState(false);

  const generateBulkData = async () => {
    setIsSeeding(true);
    try {
      await api.post('/events/seed');
      fetchRawData(activeRawTab);
      fetchEvents();
    } catch (err) {
      console.error('Seeding failed', err);
    } finally {
      setIsSeeding(false);
    }
  };

  return (
    <div className="h-full flex flex-col bg-[#fdfdfd]">
      {/* 🚀 Sleek Header Bar */}
      <div className="px-8 py-6 border-b border-slate-50 bg-white sticky top-0 z-[1000] flex items-center justify-between">
        <div className="flex items-center gap-4">
           <div className="p-3 bg-[#2e3a59] rounded-2xl text-white shadow-xl shadow-slate-900/10">
              <Database className="w-5 h-5" />
           </div>
           <div>
              <h1 className="text-xl font-black text-[#2e3a59] tracking-tight">Raw Forensic Database</h1>
              <div className="flex items-center gap-2">
                 <Radio className="w-3 h-3 text-skylark-orange animate-pulse" />
                 <span className="text-[10px] font-bold text-slate-300 uppercase tracking-widest">DESC SQL View • ridgeway-01</span>
              </div>
           </div>
        </div>

        <div className="flex items-center gap-2">
           <button 
             disabled={isSeeding}
             onClick={generateBulkData}
             className="px-6 py-2 bg-orange-50 text-skylark-orange text-[10px] font-bold uppercase tracking-widest rounded-xl hover:bg-orange-100 transition-all border border-orange-100 flex items-center gap-2"
           >
              <Database className="w-3 h-3" />
              {isSeeding ? 'Seeding...' : 'Generate Forensic Data'}
           </button>
           <button 
             disabled={isScanning}
             onClick={triggerScan}
             className={clsx(
               "px-6 py-2 rounded-xl text-[10px] font-bold uppercase tracking-widest transition-all",
               isScanning ? "bg-slate-100 text-slate-400" : "bg-[#2e3a59] text-white hover:bg-black shadow-lg shadow-slate-900/10"
             )}
           >
              {isScanning ? 'Syncing...' : 'Trigger AI Hub'}
           </button>
        </div>
      </div>

      {/* 📋 Navigation Tabs */}
      <div className="px-8 pt-4 bg-white border-b border-slate-50 overflow-x-auto scrollbar-hide flex gap-8">
        {(['sensors', 'access', 'vehicles', 'drones'] as RawTab[]).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveRawTab(tab)}
            className={clsx(
              "pb-4 text-xs font-bold uppercase tracking-widest transition-all border-b-2",
              activeRawTab === tab ? "border-skylark-orange text-skylark-orange" : "border-transparent text-slate-300 hover:text-slate-500"
            )}
          >
            {tab === 'access' ? 'Access Control' : tab}
          </button>
        ))}
      </div>

      <div className="flex-1 p-8 overflow-auto">
        {/* 🏢 Data Grid View */}
        <div className="bg-white rounded-[2.5rem] border border-slate-100 shadow-xl overflow-hidden flex flex-col">
           {/* Grid Action Bar */}
           <div className="p-6 border-b border-slate-50 flex items-center justify-between bg-slate-50/50">
              <div className="flex items-center gap-4 bg-white border border-slate-100 rounded-2xl px-4 py-2 shadow-sm shrink-0">
                 <Search className="w-4 h-4 text-slate-300" />
                 <input placeholder="Filter results..." className="bg-transparent border-none outline-none text-xs font-medium text-[#2e3a59]" />
              </div>
              <div className="flex items-center gap-2">
                 <button className="p-2.5 bg-white border border-slate-100 rounded-xl text-slate-400 hover:text-skylark-orange shadow-sm"><ExternalLink className="w-4 h-4" /></button>
                 <button onClick={() => fetchRawData(activeRawTab)} className="p-2.5 bg-white border border-slate-100 rounded-xl text-slate-400 hover:text-skylark-orange shadow-sm"><Activity className="w-4 h-4" /></button>
              </div>
           </div>

           <div className="overflow-x-auto">
              <table className="w-full text-left">
                 <thead>
                    <tr className="bg-slate-50/20 text-[10px] font-black text-slate-400 uppercase tracking-wider">
                       {renderTableHeaders().map(h => (
                         <th key={h} className="py-5 px-6 font-black">{h}</th>
                       ))}
                    </tr>
                 </thead>
                 <tbody className="divide-y divide-slate-50">
                    {rawData.map((item, idx) => (
                      <tr key={item.id} className="hover:bg-slate-50/50 transition-colors group">
                        {renderRow(item)}
                      </tr>
                    ))}
                 </tbody>
              </table>

              {rawData.length === 0 && !isLoading && (
                <div className="text-center py-32 space-y-4">
                   <ShieldAlert className="w-12 h-12 text-slate-100 mx-auto" />
                   <p className="text-xs font-bold text-slate-300 uppercase tracking-widest">No forensic data found in this partition</p>
                </div>
              )}

              {isLoading && (
                <div className="text-center py-32 space-y-4">
                   <Activity className="w-12 h-12 text-skylark-orange/20 mx-auto animate-pulse" />
                   <p className="text-xs font-bold text-slate-200 uppercase tracking-widest">Querying SQL Pool...</p>
                </div>
              )}
           </div>
        </div>
      </div>
    </div>
  );
}
