import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface StandardResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

export interface Goal {
  id: number;
  family_id: string;
  title: string;
  description: string | null;
  category: 'PERSONAL' | 'ACADEMIC' | 'FINANCIAL' | 'HEALTH' | 'HOUSEHOLD';
  progress: number;
  deadline: string | null;
  ai_recommendation: string | null;
  created_at: string;
  updated_at: string;
}

export interface HabitLog {
  id: number;
  habit_id: number;
  date: string;
  completed: boolean;
  created_at: string;
}

export interface Habit {
  id: number;
  family_id: string;
  title: string;
  category: 'WATER' | 'EXERCISE' | 'READING' | 'MEDITATION' | 'STUDY' | 'CODING' | 'CUSTOM';
  streak: number;
  max_streak: number;
  created_at: string;
  updated_at: string;
  logs: HabitLog[];
}

export interface DigitalTwin {
  id: number;
  family_id: string;
  planning_score: number;
  routine_consistency: number;
  goal_completion: number;
  time_utilization: number;
  stress_level: number;
  productivity: number;
  updated_at: string;
}

export interface CalendarEvent {
  id: number;
  title: string;
  description: string | null;
  event_type: string;
  start_datetime: string;
  end_datetime: string;
  all_day: boolean;
  location: string | null;
  status: string;
  priority: string;
  source: string;
  plan_id: number | null;
}

export interface TimelineResponse {
  timeline: Array<{
    id: number;
    title: string;
    description: string | null;
    start: string;
    end: string;
    type: string;
    location: string | null;
    member: string;
    priority: string;
  }>;
  schedule_health: number;
}

export interface Recommendation {
  type: 'CONFLICT' | 'OPTIMIZATION' | 'GOAL_DEADLINE';
  title: string;
  suggestion: string;
  action_type: string;
  target_id: number;
}

export interface PlannerAgentResponse {
  ai_response: string;
  action_items: string[];
  execution_trace: {
    intent: string;
    capabilities: string[];
    agents_used: string[];
    tools_used: string[];
    database_tables_accessed: string[];
    execution_time_ms: number;
    confidence: number;
    explanation?: {
      reason: string;
      factors_considered?: string[];
    };
  };
}

export interface Task {
  id: number;
  plan_id: number;
  title: string;
  description: string | null;
  due_date: string | null;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';
  estimated_cost: number;
}

export default api;
