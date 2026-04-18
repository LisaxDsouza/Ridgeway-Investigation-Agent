'use client';

import React from 'react';
import { Plus, Search, Library, Clock, MessageSquare, Zap, User } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useIncidentStore } from '@/lib/store';
import { clsx } from 'clsx';

export default function Shell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { incidents, selectIncident, selectedIncidentId } = useIncidentStore();

  return (
    <div className="flex h-screen bg-[#f1f3f6] p-4 lg:p-10 relative overflow-hidden">
      {/* Background Decorative Bubbles */}
      <div className="absolute top-[-100px] right-[-100px] w-96 h-96 bg-skylark-orange/10 rounded-full blur-3xl p-10 animate-pulse" />
      <div className="absolute bottom-[-150px] left-[200px] w-[500px] h-[500px] bg-orange-200/20 rounded-full blur-[100px]" />
      <div className="absolute top-[40%] left-[-50px] w-32 h-32 bg-skylark-orange/5 rounded-full blur-2xl" />

      {/* 🚀 Minimalist Sidebar */}
      <aside className="w-80 bg-white/80 backdrop-blur-md rounded-l-[2.5rem] flex flex-col p-8 border-r border-orange-100 shrink-0 z-10">
        <div className="flex items-center gap-3 mb-10 px-2">
           <div className="w-10 h-10 bg-skylark-orange rounded-xl flex items-center justify-center text-white shadow-lg shadow-orange-500/20">
              <Zap className="w-6 h-6 fill-white" />
           </div>
           <span className="font-extrabold text-2xl text-[#2e3a59] tracking-tight">Skylark</span>
        </div>

        <button className="flex items-center gap-3 w-full p-4 bg-skylark-orange text-white rounded-2xl font-bold text-sm shadow-xl shadow-orange-500/20 hover:bg-skylark-orange-hover transition-all group mb-8">
           <Plus className="w-5 h-5 group-hover:rotate-90 transition-transform" />
           New Investigation
        </button>

        <nav className="flex-1 space-y-2 overflow-y-auto pr-2 scrollbar-hide">
           <div className="flex items-center gap-3 p-4 text-slate-400 font-bold text-xs uppercase tracking-widest">
              <Search className="w-4 h-4" />
              Search Investigations
           </div>
           <div className="flex items-center gap-3 p-4 text-slate-400 font-bold text-xs uppercase tracking-widest mb-4">
              <Library className="w-4 h-4" />
              Library
           </div>

           <p className="px-4 text-[10px] font-bold text-slate-300 uppercase tracking-widest mb-2 mt-8">Recent Investigations</p>
           {incidents.slice(0, 8).map((inc) => (
             <button
               key={inc.id}
               onClick={() => selectIncident(inc.id)}
               className={clsx(
                 "flex items-center gap-4 w-full p-4 rounded-2xl transition-all text-left group",
                 selectedIncidentId === inc.id 
                   ? "bg-orange-50 text-skylark-orange" 
                   : "text-slate-500 hover:bg-slate-50"
               )}
             >
               <Clock className={clsx("w-5 h-5 shrink-0", selectedIncidentId === inc.id ? "text-skylark-orange" : "text-slate-300")} />
               <span className="text-sm font-semibold truncate">REF-{inc.id.slice(0, 6)}: {inc.hypothesis.slice(0, 20)}...</span>
             </button>
           ))}
        </nav>

      </aside>

      {/* 🖥️ Main Interactive Stage */}
      <section className="flex-1 bg-white/95 backdrop-blur-sm rounded-r-[2.5rem] flex flex-col overflow-hidden relative border-4 border-skylark-orange/20 z-10">
        <div className="flex-1 overflow-auto p-12">
          {children}
        </div>
      </section>
    </div>
  );
}
