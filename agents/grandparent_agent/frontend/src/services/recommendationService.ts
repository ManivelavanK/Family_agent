import { api, isBackendUnavailable } from './api';
import { Recommendation } from '../types';
import { mockRecommendations } from '../data/mockData';

export const recommendationService = {
  getRecommendations: async (): Promise<Recommendation[]> => {
    try {
      const response = await api.get('/recommendation/');
      // The backend returns a RecommendationResponse object: { summary: string, recommendations: RecommendationItem[] }
      // Our Axios interceptor unwraps the outer APIResponse wrapper, so response.data holds the RecommendationResponse object.
      const data = response.data;
      const list = data.recommendations || [];
      
      return list.map((item: any, idx: number) => ({
        id: `rec-${idx}-${Date.now()}`,
        category: item.category || 'General',
        title: item.suggestion || 'Wellness Update',
        content: item.rationale || 'Monitor your parameters.',
        priority: (item.category === 'Health Warning' || item.suggestion.toLowerCase().includes('critical') || item.suggestion.toLowerCase().includes('elevated') || item.suggestion.toLowerCase().includes('reduce')) ? 'High' : 'Medium',
        reason: item.rationale || 'Health logs checked.',
        created_at: new Date().toISOString()
      }));
    } catch (e) {
      if (isBackendUnavailable(e)) {
        const local = localStorage.getItem('grandparent_recommendations');
        if (!local) {
          localStorage.setItem('grandparent_recommendations', JSON.stringify(mockRecommendations));
          return mockRecommendations;
        }
        return JSON.parse(local);
      }
      throw e;
    }
  }
};
