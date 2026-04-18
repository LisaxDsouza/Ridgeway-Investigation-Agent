'use client';

import React, { useEffect } from 'react';
import { useIncidentStore } from '@/lib/store';
import { ShieldAlert, CheckCircle2, AlertCircle, Clock, ChevronRight } from 'lucide-react';
import { clsx } from 'clsx';

export default function IncidentList() {
  const { incidents, fetchIncidents, selectIncident, selectedIncidentId, isLoading } = useIncidentStore();

  useEffect(() => {
    fetchIncidents();
  }, []);

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between mb-8">
        <h3 className="text-xl font-bold text-[#2e3a59]">Active Investigations</h3>
        <div className="flex items-center gap-2 bg-orange-50 text-skylark-orange px-4 py-2 rounded-2xl border border-orange-100 shadow-sm">
           <AlertCircle className="w-4 h-4" />
           <span className="text-xs font-bold uppercase tracking-wider">{incidents.length} Critical Events</span>
        </div>
      </div>

      <div className="flex gap-6 overflow-x-auto pb-4 scrollbar-hide">
        {isLoading ? (
          <div className="flex gap-6">
             {[1,2].map(i => (
                <div key={i} className="w-[450px] h-[220px] bg-slate-50 animate-pulse rounded-[2.5rem]" />
             ))}
          </div>
        ) : incidents.length === 0 ? (
          <div className="bg-slate-50 w-full h-[220px] rounded-[2.5rem] flex flex-col items-center justify-center border-2 border-dashed border-slate-100">
             <CheckCircle2 className="w-10 h-10 text-slate-200 mb-2" />
             <p className="text-slate-400 font-medium">All systems normal.</p>
          </div>
        ) : (
          incidents.map((incident) => (
            <button
              key={incident.id}
              onClick={() => selectIncident(incident.id)}
              className={clsx(
                "w-[500px] shrink-0 p-8 rounded-[2.5rem] transition-all duration-500 text-left relative overflow-hidden group border-2",
                selectedIncidentId === incident.id
                  ? "bg-white border-skylark-orange shadow-2xl scale-[1.02]"
                  : "bg-white border-slate-50 hover:border-slate-200 shadow-skylark"
              )}
            >
              <div className="flex justify-between items-start relative z-10">
                <div className="flex items-center gap-3">
                   <div className={clsx(
                       "p-4 rounded-3xl transition-colors",
                       selectedIncidentId === incident.id ? "bg-skylark-orange text-white" : "bg-slate-100 text-slate-400"
                   )}>
                      <ShieldAlert className="w-8 h-8" />
                   </div>
                   <div>
                      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Incident Report</p>
                      <p className="text-lg font-bold text-[#2e3a59]">REF-{incident.id.slice(0, 6)}</p>
                   </div>
                </div>
                <div className="bg-slate-50 px-4 py-2 rounded-2xl flex items-center gap-2">
                   <div className="w-2 h-2 rounded-full bg-skylark-orange animate-pulse" />
                   <span className="text-xs font-bold text-[#2e3a59]">{Math.round(incident.confidence_score * 100)}% Match</span>
                </div>
              </div>

              <p className="mt-8 text-slate-600 font-medium line-clamp-2 text-lg leading-relaxed relative z-10">
                {incident.hypothesis}
              </p>

              <div className="mt-8 flex items-center justify-between relative z-10">
                <div className="flex items-center gap-3 text-slate-400">
                   <div className="flex items-center gap-1 text-xs">
                      <Clock className="w-4 h-4" />
                      <span>Today, 06:10 AM</span>
                   </div>
                </div>
                <ChevronRight className={clsx(
                    "w-6 h-6 transition-transform group-hover:translate-x-1",
                    selectedIncidentId === incident.id ? "text-skylark-orange" : "text-slate-200"
                )} />
              </div>

              {/* Decorative Background Element */}
              {selectedIncidentId === incident.id && (
                  <div className="absolute top-[-50px] right-[-50px] w-64 h-64 bg-orange-50 rounded-full opacity-30 blur-3xl pointer-events-none" />
              )}
            </button>
          ))
        )}
      </div>
    </div>
  );
}
