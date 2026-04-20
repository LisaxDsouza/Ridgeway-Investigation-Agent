import { create } from 'zustand';
import api from './api';

export interface Incident {
  id: string;
  hypothesis: string;
  confidence_score: number;
  confidence_level: string;
  confidence_rationale: string;
  recommended_action: string;
  reasoning_trace: any;
  cluster_centroid_lat: number;
  cluster_centroid_lon: number;
  created_at: string;
}

export interface Briefing {
  id: string;
  briefing_date: string;
  q1_summary: string;
  export_text: string;
  created_at: string;
}

export interface UnifiedEvent {
  source: 'sensor' | 'access' | 'vehicle' | 'drone';
  id: string;
  time: string;
  zone: string;
  type: string;
  severity: 'low' | 'medium' | 'high';
  lat?: number;
  lon?: number;
}

interface IncidentState {
  incidents: Incident[];
  briefings: Briefing[];
  unifiedEvents: UnifiedEvent[];
  selectedIncidentId: string | null;
  activeTab: 'dashboard' | 'morning-report' | 'control-room' | 'situation-map';
  isLoading: boolean;
  isScanning: boolean;
  error: string | null;
  
  fetchIncidents: () => Promise<void>;
  fetchBriefings: () => Promise<void>;
  fetchEvents: () => Promise<void>;
  selectIncident: (id: string | null) => void;
  setActiveTab: (tab: 'dashboard' | 'morning-report' | 'control-room' | 'situation-map') => void;
  triggerScan: () => Promise<void>;
  reviewIncident: (id: string, note: string, status: string) => Promise<void>;
}

export const useIncidentStore = create<IncidentState>((set, get) => ({
  incidents: [],
  briefings: [],
  unifiedEvents: [],
  selectedIncidentId: null,
  activeTab: 'dashboard',
  isLoading: false,
  isScanning: false,
  error: null,

  fetchIncidents: async () => {
    set({ isLoading: true });
    try {
      const response = await api.get('/incidents/');
      set({ incidents: response.data, isLoading: false });
    } catch (err) {
      set({ error: 'Failed to fetch incidents', isLoading: false });
    }
  },

  fetchBriefings: async () => {
    try {
      const response = await api.get('/briefings/');
      set({ briefings: response.data });
    } catch (err) {
      console.error('Failed to fetch briefings', err);
    }
  },

  fetchEvents: async () => {
    try {
      const response = await api.get('/events/');
      set({ unifiedEvents: response.data.events });
    } catch (err) {
      console.error('Failed to fetch events', err);
    }
  },

  setActiveTab: (tab) => set({ activeTab: tab, selectedIncidentId: null }),

  selectIncident: (id) => {
    set({ selectedIncidentId: id, activeTab: id ? 'dashboard' : get().activeTab });
  },

  triggerScan: async () => {
    set({ isScanning: true });
    try {
      // 1. Trigger the investigation
      const invResponse = await api.post('/investigate/');
      const jobId = invResponse.data.job_id;
      
      // 2. Simple polling or wait (for demo, we wait 5s then refresh)
      await new Promise(resolve => setTimeout(resolve, 5000));
      
      // 3. Generate the briefing
      await api.post('/briefings/generate');
      
      // 4. Refresh everything
      await get().fetchIncidents();
      await get().fetchBriefings();
      set({ isScanning: false });
    } catch (err) {
      set({ isScanning: false, error: 'Scan failed' });
    }
  },

  reviewIncident: async (id: string, note: string, status: string) => {
    try {
      await api.patch(`/incidents/${id}/review`, {
        human_note: note,
        review_status: status,
      });
      get().fetchIncidents();
    } catch (err) {
      set({ error: 'Failed to update review' });
    }
  },
}));
