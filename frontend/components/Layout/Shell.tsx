'use client';

import React, { useEffect } from 'react';
import { Plus, Search, Library, Clock, Zap, LayoutDashboard, FileText, Settings, Radio, Map } from 'lucide-react';
import { useIncidentStore } from '@/lib/store';
import { clsx } from 'clsx';
import Dashboard from '../Dashboard/Dashboard';
import ControlRoom from '../Dashboard/ControlRoom';
import ForensicConsole from '../Dashboard/ForensicConsole';
import dynamic from 'next/dynamic';

const SituationMap = dynamic(() => import('../Dashboard/SituationMap'), { 
  ssr: false,
  loading: () => (
    <div className="h-full flex items-center justify-center bg-slate-50 text-slate-400 font-bold animate-pulse">
      Loading Tactical Map...
    </div>
  )
});

export default function Shell({ children }: { children: React.ReactNode }) {
  const { 
    incidents, 
    selectIncident, 
    selectedIncidentId, 
    activeTab, 
    setActiveTab,
    fetchIncidents 
  } = useIncidentStore();

  useEffect(() => {
    fetchIncidents();
  }, [fetchIncidents]);

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'control-room':
        return <ControlRoom />;
      case 'situation-map':
        return <SituationMap />;
      case 'dashboard':
      default:
        // If an incident is selected OR if we have incidents but none selected, show the deep forensic console
        if (selectedIncidentId) {
          return <ForensicConsole />;
        }
        
        // If we have incidents but none selected, auto-show the latest one
        if (incidents.length > 0) {
           return <ForensicConsole />;
        }
        
        return <Dashboard />;
    }
  };

  return (
    <div className="flex h-screen bg-[#f1f3f6] p-4 lg:p-10 relative overflow-hidden font-sans">
      {/* Background Decorative Bubbles */}
      <div className="absolute top-[-100px] right-[-100px] w-96 h-96 bg-skylark-orange/10 rounded-full blur-3xl p-10 animate-pulse" />
      <div className="absolute bottom-[-150px] left-[200px] w-[500px] h-[500px] bg-orange-200/20 rounded-full blur-[100px]" />
      <div className="absolute top-[40%] left-[-50px] w-32 h-32 bg-skylark-orange/5 rounded-full blur-2xl" />

      {/* 🚀 Minimalist Sidebar */}
      <aside className="w-80 bg-white/80 backdrop-blur-md rounded-l-[2.5rem] flex flex-col p-8 border-r border-orange-100 shrink-0 z-10">
        <div className="flex items-center gap-3 mb-10 px-2 cursor-pointer" onClick={() => setActiveTab('dashboard')}>
           <div className="w-10 h-10 bg-skylark-orange rounded-xl flex items-center justify-center text-white shadow-lg shadow-orange-500/20">
              <Zap className="w-6 h-6 fill-white" />
           </div>
           <span className="font-extrabold text-2xl text-[#2e3a59] tracking-tight">Skylark</span>
        </div>

        <nav className="flex-1 space-y-2 overflow-y-auto pr-2 scrollbar-hide">
           <p className="px-4 text-[10px] font-bold text-slate-300 uppercase tracking-widest mb-4">Core Modules</p>
           
           <button 
             onClick={() => setActiveTab('dashboard')}
             className={clsx(
               "flex items-center gap-3 w-full p-4 rounded-2xl font-bold text-sm transition-all group",
               activeTab === 'dashboard' ? "bg-skylark-orange text-white shadow-xl shadow-orange-500/20" : "text-slate-500 hover:bg-slate-50"
             )}
           >
              <LayoutDashboard className="w-5 h-5" />
              Intelligence Dashboard
           </button>


           <button 
             onClick={() => setActiveTab('control-room')}
             className={clsx(
               "flex items-center gap-3 w-full p-4 rounded-2xl font-bold text-sm transition-all group",
               activeTab === 'control-room' ? "bg-skylark-orange text-white shadow-xl shadow-orange-500/20" : "text-slate-500 hover:bg-slate-50"
             )}
           >
              <Radio className="w-5 h-5" />
              Forensic Control Room
           </button>

           <button 
             onClick={() => setActiveTab('situation-map')}
             className={clsx(
               "flex items-center gap-3 w-full p-4 rounded-2xl font-bold text-sm transition-all group",
               activeTab === 'situation-map' ? "bg-skylark-orange text-white shadow-xl shadow-orange-500/20" : "text-slate-500 hover:bg-slate-50"
             )}
           >
              <Map className="w-5 h-5" />
              Situation Map
           </button>

           <p className="px-4 text-[10px] font-bold text-slate-300 uppercase tracking-widest mb-2 mt-8">Recent Investigations</p>
           {incidents.slice(0, 6).map((inc) => (
             <button
               key={inc.id}
               onClick={() => selectIncident(inc.id)}
               className={clsx(
                 "flex items-center gap-4 w-full p-4 rounded-2xl transition-all text-left group",
                 selectedIncidentId === inc.id 
                   ? "bg-orange-50 text-skylark-orange font-bold" 
                   : "text-slate-500 hover:bg-slate-50"
               )}
             >
               <Clock className={clsx("w-5 h-5 shrink-0", selectedIncidentId === inc.id ? "text-skylark-orange" : "text-slate-300")} />
               <span className="text-xs truncate">REF-{inc.id.slice(0, 8)}</span>
             </button>
           ))}
        </nav>

        <div className="mt-auto pt-6 border-t border-slate-50">
           <button className="flex items-center gap-3 p-4 text-slate-400 font-bold text-xs uppercase tracking-widest hover:text-slate-600 transition-colors">
              <Settings className="w-4 h-4" />
              Settings
           </button>
        </div>
      </aside>

      {/* 🖥️ Main Interactive Stage */}
      <section className="flex-1 bg-white/95 backdrop-blur-sm rounded-r-[2.5rem] flex flex-col overflow-hidden relative border-4 border-skylark-orange/20 z-10 shadow-2xl">
        <div className="flex-1 overflow-auto">
          {renderActiveTab()}
        </div>
      </section>
    </div>
  );
}
