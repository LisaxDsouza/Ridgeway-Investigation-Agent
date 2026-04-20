'use client';

import React, { useState } from 'react';
import { Send, User, Sparkles, Paperclip, Mic } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import api from '@/lib/api';
import { clsx } from 'clsx';

export default function IncidentChat({ incidentId }: { incidentId: string }) {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    
    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    try {
      const response = await api.post(`/incidents/${incidentId}/chat`, { message: input });
      setMessages(prev => [...prev, { role: 'assistant', content: response.data.answer }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: "I'm sorry, I'm having trouble connecting to the investigation log." }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white relative">
      {/* 💬 Conversation Thread */}
      <div className="flex-1 overflow-auto p-12 space-y-10 scrollbar-hide pb-40">
        {messages.length === 0 && (
          <div className="max-w-5xl mx-auto py-20 text-center space-y-6">
            <div className="w-16 h-16 bg-orange-50 rounded-2xl flex items-center justify-center mx-auto shadow-sm">
               <Sparkles className="w-8 h-8 text-skylark-orange" />
            </div>
            <h3 className="text-2xl font-bold text-[#2e3a59]">Investigation Context Loaded</h3>
            <p className="text-slate-400 font-medium leading-relaxed max-w-lg mx-auto">
              I have retrieved all sensor events and shift logs for this incident. 
              How would you like to proceed with the analysis?
            </p>
          </div>
        )}
        
        {messages.map((m, i) => (
          <div key={i} className={clsx(
              "flex gap-8 max-w-6xl mx-auto",
              m.role === 'user' ? "flex-row-reverse" : ""
          )}>
            <div className={clsx(
                "w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 border transition-all shadow-sm",
                m.role === 'user' ? "bg-white border-slate-100 text-slate-400" : "bg-orange-50 border-orange-100 text-skylark-orange"
            )}>
              {m.role === 'user' ? <User className="w-6 h-6" /> : <Sparkles className="w-6 h-6" />}
            </div>
            <div className={clsx(
                "p-8 rounded-[2.5rem] text-base leading-relaxed border transition-all shadow-sm max-w-[80%]",
                m.role === 'user' 
                  ? "bg-white border-slate-50 text-slate-700 rounded-tr-none" 
                  : "bg-slate-50/50 border-slate-50 text-[#2e3a59] rounded-tl-none font-medium"
            )}>
              {m.role === 'assistant' ? (
                <div className="markdown-container prose-sm">
                  <ReactMarkdown>{m.content}</ReactMarkdown>
                </div>
              ) : m.content}
            </div>
          </div>
        ))}
        
        {isTyping && (
          <div className="flex gap-8 max-w-6xl mx-auto animate-pulse">
             <div className="w-12 h-12 rounded-2xl bg-orange-50 border border-orange-100 text-skylark-orange flex items-center justify-center">
                <Sparkles className="w-6 h-6" />
             </div>
             <div className="bg-slate-50/50 p-8 rounded-[2.5rem] rounded-tl-none text-slate-400 text-base">Analyzing data...</div>
          </div>
        )}
      </div>

      {/* ⌨️ Minimalist Input Bar (Floating at bottom of container) */}
      <div className="absolute bottom-10 left-12 right-12">
        <div className="w-full bg-white shadow-2xl shadow-slate-200 rounded-[2.5rem] border border-slate-100 p-4 transition-all focus-within:ring-4 focus-within:ring-orange-100/50">
          <div className="flex items-center gap-4 px-6 pt-2">
             <input 
               value={input}
               onChange={(e) => setInput(e.target.value)}
               onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), sendMessage())}
               placeholder="Ask for site details or draft a summary..."
               className="flex-1 bg-transparent border-none text-lg outline-none text-[#2e3a59] placeholder:text-slate-300 font-medium h-12"
             />
          </div>
          
          <div className="flex items-center justify-between mt-4">
             <button className="flex items-center gap-2 px-5 py-2.5 bg-slate-50 hover:bg-slate-100 rounded-[1.5rem] text-slate-400 text-xs font-bold transition-all border border-slate-100">
                <Paperclip className="w-4 h-4" />
                Attach
             </button>
             
             <div className="flex items-center gap-2">
                <button 
                  onClick={sendMessage}
                  disabled={!input.trim()}
                  className={clsx(
                      "p-4 rounded-full transition-all flex items-center justify-center text-white shadow-lg",
                      input.trim() ? "bg-skylark-orange scale-100 hover:scale-105" : "bg-slate-100 text-slate-300 scale-95"
                  )}
                >
                  <Send className="w-5 h-5 fill-white" />
                </button>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
