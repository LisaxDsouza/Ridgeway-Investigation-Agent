'use client';

import React from 'react';
import { useIncidentStore } from '@/lib/store';
import { 
  ShieldCheck, MoreHorizontal, Eraser, Plus, 
  ShieldAlert
} from 'lucide-react';
import IncidentChat from '../Review/IncidentChat';
import { clsx } from 'clsx';

export default function ForensicConsole() {
  const { incidents, selectedIncidentId, reviewIncident } = useIncidentStore();
  const incidentSnapshot = incidents.find(i => i.id === selectedIncidentId);
  const incident = incidentSnapshot || incidents[0];

  if (!incident) {
    return (
      <div className="h-full bg-slate-50/10 rounded-[2.5rem] border-2 border-dashed border-slate-100 flex flex-col items-center justify-center text-slate-400 gap-6 p-12">
        <div className="w-32 h-32 bg-white rounded-[3rem] shadow-skylark flex items-center justify-center animate-pulse">
           <BrainCircuit className="w-16 h-16 text-slate-100" />
        </div>
        <div className="text-center space-y-2">
           <p className="text-xl font-extrabold text-[#2e3a59]">Investigation Terminal Idle</p>
           <p className="text-sm font-medium text-slate-400">Select an active incident from the sidebar to open the forensic console.</p>
        </div>
      </div>
    );
  }

  // Parse reasoning trace safely
  let traceData = typeof incident.reasoning_trace === 'string' 
    ? JSON.parse(incident.reasoning_trace) 
    : (incident.reasoning_trace || []);
  
  // Handle case where trace is wrapped in an object like { steps: [...] }
  const rawTrace = Array.isArray(traceData) 
    ? traceData 
    : (traceData.steps || []);

  return (
    <div className="h-full p-10 bg-slate-50/30 overflow-hidden">
      {/* Main Chat Interface (Expanded) */}
      <div className="h-full bg-white rounded-[3rem] shadow-skylark border border-slate-100 flex flex-col relative overflow-hidden">
        <div className="p-8 border-b border-slate-50 flex items-center justify-between bg-white/50 backdrop-blur-md sticky top-0 z-10">
           <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-orange-100 rounded-2xl flex items-center justify-center text-skylark-orange">
                 <ShieldAlert className="w-6 h-6" />
              </div>
              <div>
                 <h3 className="font-extrabold text-[#2e3a59] flex items-center gap-2 text-lg">
                   Investigation: REF-{incident.id.slice(0, 8)}
                   <div className="px-2.5 py-1 bg-orange-50 text-skylark-orange rounded-lg text-[9px] font-black uppercase tracking-widest border border-orange-100">
                      {incident.confidence_level} Confidence
                   </div>
                 </h3>
                 <p className="text-xs text-slate-400 font-medium italic">Logic: {incident.recommended_action}</p>
              </div>
           </div>
           
           <div className="flex items-center gap-3">
              <button 
                onClick={() => reviewIncident(incident.id, 'Confirmed baseline via forensic override.', 'resolved')}
                className="px-6 py-3 bg-skylark-orange text-white rounded-2xl font-bold text-xs shadow-xl shadow-orange-500/20 hover:scale-105 active:scale-95 transition-all flex items-center gap-2"
              >
                <ShieldCheck className="w-4 h-4 fill-white" />
                Accept AI Logic
              </button>
              
              <div className="h-8 w-px bg-slate-100 mx-2" />
              
              <button className="p-3 bg-slate-50 rounded-2xl text-slate-400 hover:text-slate-600 border border-slate-100 transition-colors">
                 <MoreHorizontal className="w-5 h-5" />
              </button>
           </div>
        </div>

        {/* The Chat Area (Maya's Brain Output) */}
        <div className="flex-1 overflow-hidden">
           <IncidentChat incidentId={incident.id} />
        </div>

        {/* Console Controls */}
        <div className="absolute left-8 bottom-32 flex flex-col gap-4">
           <button className="p-4 bg-white shadow-2xl shadow-slate-200 rounded-2xl border border-slate-100 hover:bg-slate-50 text-slate-600 transition-all hover:-translate-y-1">
              <Eraser className="w-6 h-6" />
           </button>
           <button className="p-4 bg-[#2e3a59] shadow-2xl shadow-[#2e3a59]/20 rounded-2xl text-white transition-all hover:scale-110 active:scale-90">
              <Plus className="w-6 h-6" />
           </button>
        </div>
      </div>
    </div>
  );
}
