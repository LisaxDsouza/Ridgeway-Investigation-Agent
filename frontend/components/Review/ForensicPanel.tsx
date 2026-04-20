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

  // Extract trace steps and graph
  const steps = selectedIncident.reasoning_trace?.steps || [];
  const graph = selectedIncident.reasoning_trace?.evidence_graph;

  return (
    <div className="flex flex-col h-full bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
      <div className="p-6 border-b border-slate-50">
        <div className="flex justify-between items-start mb-4">
          <span className="bg-amber-50 text-amber-600 text-[10px] font-bold px-2 py-1 rounded-md uppercase tracking-wide border border-amber-100 italic">
            AI Generated Hypothesis
          </span>
          <div className="flex gap-2">
            <span className={clsx(
              "text-[10px] font-bold px-2 py-1 rounded-md uppercase",
              selectedIncident.confidence_level === 'critical' ? "bg-red-50 text-red-600 border border-red-100" :
              selectedIncident.confidence_level === 'high' ? "bg-green-50 text-green-600 border border-green-100" :
              "bg-slate-50 text-slate-600 border border-slate-100"
            )}>
              {selectedIncident.confidence_level} Confidence
            </span>
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
            <h4 className="text-[11px] font-bold text-slate-400 uppercase">Forensic Confidence</h4>
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

        {/* Evidence Graph Summary */}
        {graph && (
          <section className="bg-slate-50 rounded-2xl p-4 border border-slate-100">
            <h4 className="text-[11px] font-bold text-slate-400 uppercase mb-3 flex items-center gap-2">
              <BrainCircuit className="w-3.5 h-3.5" />
              Evidence Relationships
            </h4>
            <p className="text-xs text-slate-600 mb-3 font-medium">{graph.summary}</p>
            <div className="flex flex-wrap gap-2">
              {graph.edges.map((edge: any, i: number) => (
                <div key={i} className="bg-white px-2 py-1 rounded-lg border border-slate-200 text-[10px] text-slate-500 shadow-sm">
                  Step {edge.source + 1} <ArrowRight className="inline w-2.5 h-2.5 mx-1" /> Step {edge.target + 1}: <span className="text-slate-800 font-bold">{edge.relation}</span>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Reasoning Trace */}
        <section>
          <h4 className="text-[11px] font-bold text-slate-400 uppercase mb-4 flex items-center gap-2">
            <History className="w-3.5 h-3.5" />
            Investigation Trace
          </h4>
          <div className="space-y-6 relative before:absolute before:left-[11px] before:top-2 before:bottom-2 before:w-px before:bg-slate-50">
            {steps.map((step: any, idx: number) => (
              <div key={idx} className="relative pl-8">
                <div className="absolute left-0 top-1 w-[22px] h-[22px] bg-white border border-slate-200 rounded-full flex items-center justify-center font-bold text-[10px] text-slate-400 z-10 shadow-sm">
                  {idx + 1}
                </div>
                <div>
                  <div className="flex justify-between items-center mb-1">
                    <p className="text-[11px] font-bold text-slate-400 uppercase tracking-tight">
                      Tool Call: <span className="text-skylark-orange">{step.tool}</span>
                    </p>
                    <div className="flex gap-1.5">
                      {step.metadata?.storage_format && (
                        <span className="text-[9px] bg-slate-100 text-slate-500 px-1.5 py-0.5 rounded border border-slate-200 font-mono">
                          {step.metadata.storage_format.toUpperCase()}
                        </span>
                      )}
                      {step.metadata?.reliability && (
                        <span className="text-[9px] bg-blue-50 text-blue-500 px-1.5 py-0.5 rounded border border-blue-100 font-bold">
                          R: {Math.round(step.metadata.reliability * 100)}%
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="bg-slate-50 rounded-xl p-3 border border-slate-100">
                    <p className="text-xs text-slate-700 font-mono leading-relaxed truncate">
                      {JSON.stringify(step.input)}
                    </p>
                    <div className="mt-2 pt-2 border-t border-slate-200/20 flex items-start gap-2">
                      <Sparkles className="w-3.5 h-3.5 text-skylark-orange shrink-0 mt-0.5" />
                      <p className="text-[11px] text-slate-500 italic leading-snug">
                        {step.outcome}
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

