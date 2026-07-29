import { api, isBackendUnavailable } from './api';
import { Profile } from '../types';
import { mockProfile } from '../data/mockData';

export const profileService = {
  getProfile: async (): Promise<Profile> => {
    try {
      const response = await api.get('/profile/');
      return response.data;
    } catch (e) {
      if (isBackendUnavailable(e)) {
        const saved = localStorage.getItem('grandparent_profile');
        if (saved) return JSON.parse(saved);
        return mockProfile;
      }
      throw e;
    }
  },
  updateProfile: async (profile: Profile): Promise<Profile> => {
    try {
      const response = await api.put('/profile/update', profile);
      return response.data;
    } catch (e) {
      if (isBackendUnavailable(e)) {
        localStorage.setItem('grandparent_profile', JSON.stringify(profile));
        return profile;
      }
      throw e;
    }
  }
};
