'use client';

import React from 'react';
import { useIncidentStore } from '@/lib/store';
import { Paperclip, Mic, Send, Sparkles, LayoutGrid, FileText, Bell, Clock } from 'lucide-react';
import IncidentChat from '@/components/Review/IncidentChat';

export default function Dashboard() {
  const { selectedIncidentId, incidents } = useIncidentStore();
  const selectedIncident = incidents.find(i => i.id === selectedIncidentId);
  const [searchValue, setSearchValue] = React.useState('');

  const handleChipClick = (text: string) => {
    setSearchValue(text);
  };

  return (
    <div className="h-full flex flex-col items-center justify-center max-w-5xl mx-auto space-y-12">
      {/* 🌪️ The AI Hero Section */}
      {!selectedIncidentId ? (
        <div className="text-center space-y-4 animate-in fade-in slide-in-from-bottom-6 duration-700 w-full">
          <div className="w-20 h-20 bg-orange-50 rounded-3xl flex items-center justify-center mx-auto mb-8">
             <Sparkles className="w-10 h-10 text-skylark-orange" />
          </div>
          <h1 className="text-5xl font-extrabold text-[#2e3a59] tracking-tight">
            Welcome back, <span className="text-skylark-orange">Maya!</span>
          </h1>
          <p className="text-2xl font-medium text-slate-400">
            What can I help you <span className="text-[#2e3a59] font-bold">investigate</span> today?
          </p>
        </div>
      ) : (
        <div className="w-full flex-1 flex flex-col pt-10">
           {/* Context Header for Selected Incident */}
           <div className="flex items-center justify-between mb-8 pb-8 border-b border-slate-50">
              <div className="flex items-center gap-4">
                 <div className="p-3 bg-orange-100 rounded-2xl text-skylark-orange">
                    <LayoutGrid className="w-6 h-6" />
                 </div>
                 <div>
                    <h2 className="text-xl font-bold text-[#2e3a59]">Investigation: REF-{selectedIncidentId.slice(0, 8)}</h2>
                    <p className="text-sm text-slate-400 font-medium italic">"{selectedIncident?.hypothesis.slice(0, 100)}..."</p>
                 </div>
              </div>
              <div className="flex items-center gap-2">
                 <div className="px-4 py-2 bg-slate-50 rounded-2xl border border-slate-100 text-xs font-bold text-slate-500 flex items-center gap-2">
                    <Clock className="w-3.5 h-3.5" />
                    Today, 06:10 AM
                 </div>
              </div>
           </div>
           
           {/* Interactive Chat Frame */}
           <div className="flex-1 bg-slate-50/30 rounded-[3rem] border border-slate-100 overflow-hidden relative">
              <IncidentChat incidentId={selectedIncidentId} />
           </div>
        </div>
      )}

      {/* 🚀 Central Super Chat Input */}
      {!selectedIncidentId && (
        <div className="w-full space-y-10">
          <div className="w-full bg-white shadow-2xl shadow-slate-200 rounded-[2.5rem] border border-slate-100 p-6 transition-all focus-within:ring-4 focus-within:ring-orange-100/50">
            <div className="px-4 py-2">
               <input 
                 value={searchValue}
                 onChange={(e) => setSearchValue(e.target.value)}
                 placeholder="What do you want to build or investigate?"
                 className="w-full bg-transparent border-none text-xl outline-none text-[#2e3a59] placeholder:text-slate-300 font-medium"
               />
            </div>
            
            <div className="flex items-center justify-between mt-8">
               <button className="flex items-center gap-2 px-6 py-3 bg-slate-50 hover:bg-slate-100 rounded-2xl text-slate-400 text-sm font-bold transition-all border border-slate-100">
                  <Paperclip className="w-5 h-5" />
                  Attach Logs
               </button>
               
               <div className="flex items-center gap-4">
                  <button className="p-4 bg-skylark-orange text-white rounded-2xl shadow-xl shadow-orange-500/30 hover:bg-skylark-orange-hover hover:-translate-y-1 transition-all">
                     <Send className="w-6 h-6 fill-white" />
                  </button>
               </div>
            </div>
          </div>

          {/* Action Chips */}
          <div className="flex flex-wrap items-center justify-center gap-3">
             {[
               "Create a quick report based on my data.",
               "Search for perimeter anomalies.",
               "Summarize last night's gate logs.",
               "Draft a security brief for the team."
             ].map((text, idx) => (
               <button 
                 key={idx} 
                 onClick={() => handleChipClick(text)}
                 className="px-6 py-3 bg-white border border-slate-100 rounded-2xl text-xs font-bold text-slate-500 shadow-sm hover:border-skylark-orange hover:text-skylark-orange hover:bg-orange-50/50 transition-all"
               >
                  {text}
               </button>
             ))}
          </div>
        </div>
      )}
    </div>
  );
}
