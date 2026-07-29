import api from './api';
import type { StandardResponse, PlannerAgentResponse, DigitalTwin, TimelineResponse } from './api';

export const plannerService = {
  queryAgent: async (message: string, familyId = 'default_family'): Promise<PlannerAgentResponse> => {
    const res = await api.post<StandardResponse<PlannerAgentResponse>>('/planner/agent', { message, family_id: familyId });
    return res.data.data;
  },

  getDigitalTwin: async (familyId = 'default_family'): Promise<DigitalTwin> => {
    const res = await api.get<StandardResponse<DigitalTwin>>(`/planner/twin?family_id=${familyId}`);
    return res.data.data;
  },

  getTimeline: async (familyId = 'default_family'): Promise<TimelineResponse> => {
    const res = await api.get<StandardResponse<TimelineResponse>>(`/planner/timeline?family_id=${familyId}`);
    return res.data.data;
  }
};
