import { api, isBackendUnavailable } from './api';
import { MemoryJournal, MemoryQuizResult } from '../types';
import { mockMemoryJournals, mockMemoryQuizResults } from '../data/mockData';

const getLocalJournals = (): MemoryJournal[] => {
  const local = localStorage.getItem('grandparent_journals');
  if (!local) {
    localStorage.setItem('grandparent_journals', JSON.stringify(mockMemoryJournals));
    return mockMemoryJournals;
  }
  return JSON.parse(local);
};

const saveLocalJournals = (data: MemoryJournal[]) => {
  localStorage.setItem('grandparent_journals', JSON.stringify(data));
};

const getLocalQuizzes = (): MemoryQuizResult[] => {
  const local = localStorage.getItem('grandparent_quizzes');
  if (!local) {
    localStorage.setItem('grandparent_quizzes', JSON.stringify(mockMemoryQuizResults));
    return mockMemoryQuizResults;
  }
  return JSON.parse(local);
};

const saveLocalQuizzes = (data: MemoryQuizResult[]) => {
  localStorage.setItem('grandparent_quizzes', JSON.stringify(data));
};

export const memoryService = {
  getJournals: async (): Promise<MemoryJournal[]> => {
    // The backend stores daily cognitive logs but doesn't have an endpoint for listing multiple historical journals.
    // We merge the local storage history for seamless UI display.
    return getLocalJournals();
  },
  addJournal: async (journal: Omit<MemoryJournal, 'id' | 'date'>): Promise<MemoryJournal> => {
    try {
      const response = await api.post('/cognitive/journal', {
        entry: journal.content,
        mood: journal.mood || 'Happy'
      });
      // The response data is unwrapped by the Axios interceptor to the actual data payload (CognitiveJournalResponse)
      const resData = response.data;
      const newJournal: MemoryJournal = {
        id: resData?.id ? String(resData.id) : `j-${Date.now()}`,
        date: resData?.date || new Date().toISOString().split('T')[0],
        title: journal.title || 'Daily Log',
        content: journal.content,
        mood: journal.mood || 'Happy',
        cognitive_score: resData?.memory_score || 85
      };

      const current = getLocalJournals();
      current.unshift(newJournal);
      saveLocalJournals(current);
      return newJournal;
    } catch (e) {
      if (isBackendUnavailable(e)) {
        const current = getLocalJournals();
        const newJournal: MemoryJournal = {
          ...journal,
          id: `j-${Date.now()}`,
          date: new Date().toISOString().split('T')[0],
          cognitive_score: 85
        };
        current.unshift(newJournal);
        saveLocalJournals(current);
        return newJournal;
      }
      throw e;
    }
  },
  getQuizResults: async (): Promise<MemoryQuizResult[]> => {
    return getLocalQuizzes();
  },
  addQuizResult: async (result: Omit<MemoryQuizResult, 'id' | 'date'>): Promise<MemoryQuizResult> => {
    // The backend generates personalized quizzes but doesn't store historical quiz performance logs.
    // We save this locally.
    const current = getLocalQuizzes();
    const newQuiz: MemoryQuizResult = {
      ...result,
      id: `q-${Date.now()}`,
      date: new Date().toISOString().split('T')[0]
    };
    current.unshift(newQuiz);
    saveLocalQuizzes(current);
    return newQuiz;
  }
};
