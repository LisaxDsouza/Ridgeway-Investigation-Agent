'use client';

import React, { useEffect } from 'react';
import { useIncidentStore } from '@/lib/store';
import { Sparkles, FileText, CheckCircle2, AlertCircle, Clock, Zap, ArrowRight, ShieldCheck, Microscope } from 'lucide-react';
import { clsx } from 'clsx';

export default function MorningReport() {
  const { briefings, fetchBriefings, triggerScan, isScanning } = useIncidentStore();
  const latestBriefing = briefings[0]; // Get the most recent one

  useEffect(() => {
    fetchBriefings();
  }, [fetchBriefings]);

  if (isScanning) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-12 bg-slate-50/20">
        <div className="relative mb-12">
          <div className="w-24 h-24 bg-skylark-orange/20 rounded-full animate-ping absolute inset-0" />
          <div className="w-24 h-24 bg-white shadow-2xl rounded-3xl flex items-center justify-center relative z-10">
            <Microscope className="w-10 h-10 text-skylark-orange animate-bounce" />
          </div>
        </div>
        <h2 className="text-3xl font-extrabold text-[#2e3a59] mb-4">Maya is Investigating...</h2>
        <p className="text-slate-400 font-medium max-w-md text-center">
          Triangulating sensor signals, badge logs, and drone telemetry from the last 24 hours. Hang tight.
        </p>
      </div>
    );
  }

  if (!latestBriefing) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-12 space-y-8">
        <div className="p-8 bg-orange-50 rounded-[3rem] border-2 border-dashed border-orange-100 flex flex-col items-center gap-6">
           <FileText className="w-16 h-16 text-orange-200" />
           <div className="text-center">
              <h3 className="text-xl font-bold text-[#2e3a59]">No Report Available</h3>
              <p className="text-sm text-slate-400 font-medium mt-2">The morning forensic scan hasn't been run yet.</p>
           </div>
           <button 
             onClick={triggerScan}
             className="flex items-center gap-3 px-8 py-4 bg-skylark-orange text-white rounded-2xl font-bold shadow-xl shadow-orange-500/20 hover:scale-[1.05] transition-all"
           >
              <Zap className="w-5 h-5 fill-white" />
              Run 6:10 AM Scan
           </button>
        </div>
      </div>
    );
  }

  // Parse the 5 questions from the summary if stored in one blob (as currently implemented for demo)
  // In a real app, these might be separate fields
  const content = latestBriefing.q1_summary || latestBriefing.export_text;
  const sections = content.split(/Q\d:/).filter(Boolean);

  return (
    <div className="p-12 max-w-4xl mx-auto space-y-12 animate-in fade-in slide-in-from-bottom-8 duration-500">
      {/* Header Area */}
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-skylark-orange font-bold text-xs uppercase tracking-widest">
            <ShieldCheck className="w-4 h-4" />
            Active Investigation Briefing
          </div>
          <h1 className="text-4xl font-extrabold text-[#2e3a59] tracking-tight">
            The 6:10 AM Morning Brief
          </h1>
          <p className="text-slate-400 font-medium">
            Forensic summary for Ridgeway-01 • {new Date(latestBriefing.briefing_date).toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric' })}
          </p>
        </div>
        <button 
          onClick={triggerScan}
          className="p-4 bg-slate-50 text-slate-400 hover:text-skylark-orange hover:bg-orange-50 rounded-2xl border border-slate-100 transition-all flex items-center gap-2 font-bold text-xs"
        >
          <Zap className="w-4 h-4" />
          Re-scan
        </button>
      </div>

      {/* The 5 Pillars of Truth */}
      <div className="grid gap-6">
        {[
          "What actually happened last night?",
          "What was harmless?",
          "What deserves escalation?",
          "What did the drone check?",
          "What still needs follow-up?"
        ].map((title, idx) => (
          <div 
            key={idx} 
            className="group relative bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-sm hover:shadow-xl hover:border-orange-100 transition-all duration-300 overflow-hidden"
          >
            {/* Number Badge */}
            <div className="absolute top-0 right-0 p-8 text-slate-50 font-black text-8xl -z-0 group-hover:text-orange-50/50 transition-colors select-none">
              {idx + 1}
            </div>

            <div className="relative z-10 space-y-4">
              <div className="flex items-center gap-3">
                <div className={clsx(
                  "p-2.5 rounded-xl text-white",
                  idx === 2 ? "bg-red-400" : (idx === 1 ? "bg-green-400" : "bg-skylark-orange")
                )}>
                  <Sparkles className="w-4 h-4 fill-white" />
                </div>
                <h3 className="font-extrabold text-[#2e3a59] text-xl">{title}</h3>
              </div>
              
              <div className="text-lg text-[#2e3a59]/80 font-medium leading-relaxed max-w-2xl whitespace-pre-wrap">
                {sections[idx] ? sections[idx].trim() : "Analysis pending..."}
              </div>
            </div>
            
            <div className="absolute bottom-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-orange-100 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
        ))}
      </div>

      {/* Footer / Export */}
      <div className="pt-8 flex items-center justify-between border-t border-slate-50">
        <div className="flex items-center gap-4">
           {/* Simple Status Toggles */}
           <div className="flex items-center gap-2 px-4 py-2 bg-green-50 text-green-600 rounded-full text-[10px] font-bold uppercase tracking-wider">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Verified by Maya
           </div>
        </div>
        <button className="flex items-center gap-2 text-slate-400 font-bold text-sm hover:text-[#2e3a59] transition-colors">
          View Detail Investigation Log
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
