import api from './api';
import type { StandardResponse, Recommendation } from './api';

export const recommendationService = {
  getRecommendations: async (familyId = 'default_family'): Promise<Recommendation[]> => {
    const res = await api.get<StandardResponse<Recommendation[]>>(`/planner/recommendations?family_id=${familyId}`);
    return res.data.data;
  }
};
