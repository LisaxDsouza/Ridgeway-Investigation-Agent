import { create } from 'zustand';
import api from './api';

interface Incident {
  id: string;
  hypothesis: string;
  confidence_score: number;
  confidence_rationale: string;
  recommended_action: string;
  review_status: string;
  reasoning_trace: any[];
  cluster_center_lat: number;
  cluster_center_lon: number;
}

interface IncidentState {
  incidents: Incident[];
  selectedIncidentId: string | null;
  isLoading: boolean;
  error: string | null;
  fetchIncidents: () => Promise<void>;
  selectIncident: (id: string) => void;
  startInvestigation: () => Promise<string>;
  reviewIncident: (id: string, note: string, status: string) => Promise<void>;
}

export const useIncidentStore = create<IncidentState>((set, get) => ({
  incidents: [],
  selectedIncidentId: null,
  isLoading: false,
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

  selectIncident: (id: string) => {
    set({ selectedIncidentId: id });
  },

  startInvestigation: async () => {
    const response = await api.post('/investigate/');
    return response.data.job_id;
  },

  reviewIncident: async (id: string, note: string, status: string) => {
    try {
      await api.patch(`/incidents/${id}/review`, {
        human_note: note,
        review_status: status,
      });
      // Refresh local state
      get().fetchIncidents();
    } catch (err) {
      set({ error: 'Failed to update review' });
    }
  },
}));
