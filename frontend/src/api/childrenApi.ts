import { api } from './api';

export const childrenApi = {
  getDashboard: (childId: number = 1): Promise<any> => api.get(`/children/dashboard/${childId}`),
  getStudents: (): Promise<any> => api.get('/api/v1/students'),
  getSubjects: (): Promise<any> => api.get('/api/v1/subjects'),
  getAssignments: (): Promise<any> => api.get('/api/v1/assignments'),
  getGoals: (): Promise<any> => api.get('/api/v1/goals'),
  getExams: (): Promise<any> => api.get('/api/v1/exams'),
  getProgress: (): Promise<any> => api.get('/api/v1/progress'),
  getStudy: (): Promise<any> => api.get('/api/v1/study'),
  getScreenTime: (): Promise<any> => api.get('/children/screen-time'),
  getAttendance: (): Promise<any> => api.get('/children/attendance'),
};
