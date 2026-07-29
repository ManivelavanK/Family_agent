import api from './api';
import type { StandardResponse, CalendarEvent } from './api';

export const calendarService = {
  getEvents: async (): Promise<CalendarEvent[]> => {
    const res = await api.get<StandardResponse<CalendarEvent[]>>('/calendar/events');
    return res.data.data;
  },
  createEvent: async (event: Partial<CalendarEvent>): Promise<CalendarEvent> => {
    const res = await api.post<StandardResponse<CalendarEvent>>('/calendar/events', event);
    return res.data.data;
  },
  updateEvent: async (id: number, event: Partial<CalendarEvent>): Promise<CalendarEvent> => {
    const res = await api.put<StandardResponse<CalendarEvent>>(`/calendar/events/${id}`, event);
    return res.data.data;
  },
  deleteEvent: async (id: number): Promise<any> => {
    const res = await api.delete<StandardResponse<any>>(`/calendar/events/${id}`);
    return res.data;
  }
};
