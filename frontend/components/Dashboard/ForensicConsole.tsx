'use client';

import React from 'react';
import { useIncidentStore } from '@/lib/store';
import { BrainCircuit, History, ArrowRight, ShieldCheck, Sparkles, MoreHorizontal, Copy, Plus, Eraser, Zap } from 'lucide-react';
import IncidentChat from '../Review/IncidentChat';

export default function ForensicConsole() {
  const { incidents, selectedIncidentId, reviewIncident } = useIncidentStore();
  const incident = incidents.find(i => i.id === selectedIncidentId);

  if (!incident) {
    return (
      <div className="h-full bg-slate-50/30 rounded-[2.5rem] border-2 border-dashed border-slate-100 flex flex-col items-center justify-center text-slate-400 gap-4">
        <div className="p-6 bg-white rounded-3xl shadow-skylark">
           <BrainCircuit className="w-12 h-12 text-slate-200" />
        </div>
        <p className="text-sm font-semibold text-slate-400">Select an investigation to open Super Chat</p>
      </div>
    );
  }

  return (
    <div className="flex h-full gap-8">
      {/* 1. Main Chat Interface (Center Stage) */}
      <div className="flex-1 bg-white rounded-[2.5rem] shadow-skylark border border-slate-100 flex flex-col relative overflow-hidden">
        <div className="p-8 border-b border-slate-50 flex items-center justify-between">
           <div className="flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-green-400" />
              <h3 className="font-bold text-[#2e3a59] flex items-center gap-2 text-lg">
                Investigation Console
                <Sparkles className="w-4 h-4 text-skylark-orange" />
              </h3>
           </div>
           <button className="p-2.5 bg-slate-50 rounded-2xl text-slate-400 hover:text-slate-600 border border-slate-100 transition-colors">
              <MoreHorizontal className="w-5 h-5" />
           </button>
        </div>

        {/* The Chat Area */}
        <div className="flex-1 overflow-hidden">
           <IncidentChat incidentId={incident.id} />
        </div>

        {/* Floating Side Tools (Like the Clear Chat button in reference) */}
        <div className="absolute left-6 bottom-32 flex flex-col gap-3">
           <button className="p-3 bg-white shadow-xl rounded-2xl border border-slate-100 hover:bg-slate-50 text-slate-600 transition-all hover:-translate-y-1">
              <Eraser className="w-5 h-5" />
           </button>
           <button className="p-3 bg-[#2e3a59] shadow-xl rounded-2xl text-white transition-all hover:scale-110">
              <Plus className="w-5 h-5" />
           </button>
        </div>
      </div>

      {/* 2. Side Context (Right Deck) */}
      <div className="w-[450px] flex flex-col gap-8 shrink-0">
         {/* History / Traces (Inspired by Right Column in UI image) */}
         <div className="flex-1 bg-white rounded-[2.5rem] shadow-skylark border border-slate-100 p-8 flex flex-col overflow-hidden">
            <h4 className="font-bold text-[#2e3a59] mb-6 flex items-center justify-between">
               Investigation Log
               <div className="p-2 bg-slate-50 rounded-xl">
                  <History className="w-4 h-4 text-slate-400" />
               </div>
            </h4>
            <div className="space-y-4 overflow-y-auto pr-2 scrollbar-hide">
               {incident.reasoning_trace.map((step: any, idx: number) => (
                  <div key={idx} className="p-5 bg-slate-50 border border-slate-100 rounded-3xl group cursor-pointer hover:bg-white hover:border-skylark-orange transition-all duration-300 shadow-sm hover:shadow-lg">
                     <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2 flex items-center justify-between">
                        {step.tool}
                        <ArrowRight className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                     </p>
                     <p className="text-xs text-[#2e3a59] font-medium leading-relaxed">{step.insight}</p>
                  </div>
               ))}
            </div>
         </div>

         {/* Plan Status / Station Control (Like the Pro Plan card) */}
         <div className="bg-skylark-orange p-8 rounded-[2.5rem] shadow-2xl shadow-orange-500/30 text-white relative overflow-hidden group">
            <div className="relative z-10 flex justify-between items-start mb-6">
               <div>
                  <h5 className="text-xl font-extrabold tracking-tight">Station Ready</h5>
                  <p className="text-white/70 text-sm font-medium">Ridgeway Sector 7 Alpha</p>
               </div>
               <div className="p-3 bg-white/20 backdrop-blur-md rounded-2xl">
                  <Zap className="w-6 h-6 fill-white" />
               </div>
            </div>
            
            <button 
              onClick={() => reviewIncident(incident.id, 'Acknowledged', 'resolved')}
              className="w-full bg-[#2e3a59] text-white py-4 rounded-3xl font-bold text-sm shadow-xl transition-all hover:scale-[1.03] active:scale-95 text-center relative z-10"
            >
               Accept AI Hypothesis
            </button>

            {/* Background Blob */}
            <div className="absolute top-[-40px] right-[-40px] w-48 h-48 bg-white/10 rounded-full blur-3xl group-hover:bg-white/20 transition-all pointer-events-none" />
         </div>
      </div>
    </div>
  );
}
