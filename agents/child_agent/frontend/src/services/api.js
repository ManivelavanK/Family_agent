import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Student
  getStudent: (studentId = 1) => apiClient.get(`/students/${studentId}`).then(res => res.data),
  updateStudent: (studentId = 1, data) => apiClient.put(`/students/${studentId}`, data).then(res => res.data),
  getStudentDigitalTwin: (studentId = 1) => apiClient.get(`/students/${studentId}/digital-twin`).then(res => res.data),

  // Subjects
  getSubjects: (studentId = 1) => apiClient.get(`/subjects?student_id=${studentId}`).then(res => res.data),
  createSubject: (data) => apiClient.post('/subjects', data).then(res => res.data),
  updateSubject: (id, data) => apiClient.put(`/subjects/${id}`, data).then(res => res.data),
  deleteSubject: (id) => apiClient.delete(`/subjects/${id}`).then(res => res.data),

  // Assignments
  getAssignments: (studentId = 1) => apiClient.get(`/assignments?student_id=${studentId}`).then(res => res.data),
  createAssignment: (data) => apiClient.post('/assignments', data).then(res => res.data),
  updateAssignment: (id, data) => apiClient.put(`/assignments/${id}`, data).then(res => res.data),
  deleteAssignment: (id) => apiClient.delete(`/assignments/${id}`).then(res => res.data),

  // Study Sessions
  getStudySessions: (studentId = 1) => apiClient.get(`/study/sessions?student_id=${studentId}`).then(res => res.data),
  recordStudySession: (data) => apiClient.post('/study/sessions', data).then(res => res.data),

  // Goals
  getGoals: (studentId = 1) => apiClient.get(`/goals?student_id=${studentId}`).then(res => res.data),
  createGoal: (data) => apiClient.post('/goals', data).then(res => res.data),
  updateGoal: (id, data) => apiClient.put(`/goals/${id}`, data).then(res => res.data),
  deleteGoal: (id) => apiClient.delete(`/goals/${id}`).then(res => res.data),

  // Exams
  getExams: (studentId = 1) => apiClient.get(`/exams?student_id=${studentId}`).then(res => res.data),
  createExam: (data) => apiClient.post('/exams', data).then(res => res.data),
  updateExam: (id, data) => apiClient.put(`/exams/${id}`, data).then(res => res.data),
  deleteExam: (id) => apiClient.delete(`/exams/${id}`).then(res => res.data),
  evaluateExamReadiness: (id) => apiClient.post(`/exams/${id}/evaluate-readiness`).then(res => res.data),

  // Progress
  getProgress: (studentId = 1) => apiClient.get(`/progress?student_id=${studentId}`).then(res => res.data),

  // AI Intelligence
  queryAI: (studentId = 1, query) => apiClient.post('/ai/query', { student_id: studentId, query }).then(res => res.data),
  getStudyNow: (studentId = 1) => apiClient.get(`/ai/study-now/${studentId}`).then(res => res.data),
  getLearningPath: (studentId = 1, skillName) => apiClient.post('/ai/learning-path', { student_id: studentId, skill_name: skillName }).then(res => res.data),
  getWeaknesses: (studentId = 1) => apiClient.get(`/ai/weaknesses/${studentId}`).then(res => res.data),
  getDailyBrief: (studentId = 1) => apiClient.get(`/ai/daily-brief/${studentId}`).then(res => res.data),
  generateQuiz: (subject, topic, difficulty = "Medium") => apiClient.post('/ai/quiz', { subject, topic, difficulty }).then(res => res.data),
  
  // Cross-Agent family bridge
  getFamilySummary: (studentId = 1) => apiClient.get(`/family/child-summary/${studentId}`).then(res => res.data),
};
