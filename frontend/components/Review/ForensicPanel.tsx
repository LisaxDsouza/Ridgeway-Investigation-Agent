'use client';

import React from 'react';
import { useIncidentStore } from '@/lib/store';
import { ShieldCheck, History, ArrowRight, BrainCircuit, ExternalLink, Sparkles } from 'lucide-react';
import { clsx } from 'clsx';

import IncidentChat from './IncidentChat';

export default function ForensicPanel() {
  const { incidents, selectedIncidentId, reviewIncident } = useIncidentStore();
  const selectedIncident = incidents.find(i => i.id === selectedIncidentId);

  if (!selectedIncident) {
    return (
      <div className="h-full bg-slate-50/50 rounded-2xl border-2 border-dashed border-slate-200 flex flex-col items-center justify-center p-8 text-center">
        <div className="w-16 h-16 bg-white rounded-2xl shadow-sm flex items-center justify-center mb-4">
          <BrainCircuit className="w-8 h-8 text-slate-300" />
        </div>
        <h3 className="font-bold text-slate-800">Select an Investigation</h3>
        <p className="text-sm text-slate-400 mt-2 max-w-[200px]">
          Click an incident from the brief or map to view AI forensics.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
      <div className="p-6 border-b border-slate-50">
        <div className="flex justify-between items-start mb-4">
          <span className="bg-amber-50 text-amber-600 text-[10px] font-bold px-2 py-1 rounded-md uppercase tracking-wide border border-amber-100 italic">
            AI Generated Hypothesis
          </span>
          <div className="flex gap-2">
            <button className="p-2 hover:bg-slate-50 rounded-lg transition-colors text-slate-400">
              <ExternalLink className="w-4 h-4" />
            </button>
          </div>
        </div>
        <h2 className="text-xl font-bold text-slate-900 leading-tight">
          {selectedIncident.hypothesis}
        </h2>
      </div>

      <div className="flex-1 overflow-auto p-6 space-y-8">
        {/* Confidence Meter */}
        <section>
          <div className="flex justify-between items-end mb-2">
            <h4 className="text-[11px] font-bold text-slate-400 uppercase">Analysis Confidence</h4>
            <span className="text-sm font-bold text-slate-800">{Math.round(selectedIncident.confidence_score * 100)}%</span>
          </div>
          <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
            <div 
              className="h-full bg-skylark-orange transition-all duration-1000" 
              style={{ width: `${selectedIncident.confidence_score * 100}%` }} 
            />
          </div>
          <p className="text-xs text-slate-500 mt-2 italic">
            "{selectedIncident.confidence_rationale}"
          </p>
        </section>

        {/* Reasoning Trace: The "Vertical Timeline" */}
        <section>
          <h4 className="text-[11px] font-bold text-slate-400 uppercase mb-4 flex items-center gap-2">
            <History className="w-3.5 h-3.5" />
            Investigation Trace
          </h4>
          <div className="space-y-6 relative before:absolute before:left-[11px] before:top-2 before:bottom-2 before:w-px before:bg-slate-50">
            {selectedIncident.reasoning_trace.map((step: any, idx: number) => (
              <div key={idx} className="relative pl-8">
                <div className="absolute left-0 top-1 w-[22px] h-[22px] bg-white border border-slate-200 rounded-full flex items-center justify-center font-bold text-[10px] text-slate-400 z-10 shadow-sm">
                  {idx + 1}
                </div>
                <div>
                  <p className="text-[11px] font-bold text-slate-400 uppercase tracking-tight mb-1">
                    Tool Call: <span className="text-skylark-orange">{step.tool}</span>
                  </p>
                  <div className="bg-slate-50 rounded-xl p-3 border border-slate-100">
                    <p className="text-xs text-slate-700 font-mono leading-relaxed whitespace-pre-wrap break-all">
                      {step.query}
                    </p>
                    <div className="mt-2 pt-2 border-t border-slate-200/20 flex items-start gap-2">
                      <Sparkles className="w-3.5 h-3.5 text-skylark-orange shrink-0 mt-0.5" />
                      <p className="text-[11px] text-slate-500 italic leading-snug">
                        {step.insight}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Chat UI */}
        <section className="pt-4">
          <IncidentChat incidentId={selectedIncident.id} />
        </section>
      </div>

      {/* Action Footer */}
      <div className="p-6 bg-slate-50 border-t border-slate-100 flex gap-3">
        <button 
          onClick={() => reviewIncident(selectedIncident.id, "Verified by Supervisor", "reviewed")}
          className="flex-1 bg-white border border-slate-200 text-slate-700 font-bold text-sm py-3 rounded-xl hover:bg-slate-100 transition-colors shadow-sm"
        >
          Dismiss
        </button>
        <button 
          onClick={() => reviewIncident(selectedIncident.id, "Acknowledged", "resolved")}
          className="flex-1 bg-skylark-orange text-white font-bold text-sm py-3 rounded-xl hover:bg-skylark-orange-hover transition-colors shadow-lg shadow-orange-500/20 flex items-center justify-center gap-2"
        >
          <ShieldCheck className="w-4 h-4" />
          Accept Hypothesis
        </button>
      </div>
    </div>
  );
}
