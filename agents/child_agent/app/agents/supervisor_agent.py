import json
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.ai.llm import query_llm
from app.ai.prompts import SUPERVISOR_SYSTEM_PROMPT
import app.ai.tools as tools

logger = logging.getLogger(__name__)

class SupervisorAgent:
    def __init__(self, db: Session):
        self.db = db

    def gather_context(self, student_id: int) -> Dict[str, Any]:
        """Collects all relevant student data from the database."""
        return {
            "profile": tools.get_student_profile(self.db, student_id),
            "subjects": tools.get_subjects(self.db, student_id),
            "assignments": tools.get_assignments(self.db, student_id),
            "goals": tools.get_goals(self.db, student_id),
            "exams": tools.get_exams(self.db, student_id),
            "study_sessions": tools.get_study_sessions(self.db, student_id),
            "progress": tools.get_progress(self.db, student_id),
            "memories": tools.get_memory(self.db, student_id),
        }

    def select_agents_and_tools(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Uses LLM to understand intent and select appropriate agents/tools."""
        user_prompt = f"Student Query: '{query}'\n\nStudent DB Context:\n{json.dumps(context, default=str)}"
        
        response_str = query_llm(
            system_prompt=SUPERVISOR_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_json=True,
            temperature=0.2
        )
        
        try:
            return json.loads(response_str)
        except Exception as e:
            logger.error(f"Error parsing supervisor routing JSON: {e}. Raw response: {response_str}")
            # Fallback
            return {
                "intent": "Unknown study request",
                "agents_used": ["TutorAgent"],
                "tools_used": ["get_student_profile"],
                "requires_confirmation": False,
                "action": None
            }

    def execute(self, student_id: int, query: str) -> Dict[str, Any]:
        # 1. Gather all student context
        context = self.gather_context(student_id)
        
        # 2. Get LLM routing decision (agents to use, tools to execute)
        routing = self.select_agents_and_tools(query, context)
        
        agents_used = routing.get("agents_used", ["TutorAgent"])
        tools_used = routing.get("tools_used", [])
        intent = routing.get("intent", "Study query")
        
        # 3. Dynamic Specialist execution based on routing
        # In a real environment, we'd import and invoke specific execute methods.
        # We will dispatch to the specialist agents below.
        from app.agents.study_agent import StudyAgent
        from app.agents.planner_agent import PlannerAgent
        from app.agents.assignment_agent import AssignmentAgent
        from app.agents.goal_agent import GoalAgent
        from app.agents.progress_agent import ProgressAgent
        from app.agents.tutor_agent import TutorAgent
        from app.agents.quiz_agent import QuizAgent
        from app.agents.habit_agent import HabitAgent
        from app.agents.recommendation_agent import RecommendationAgent
        
        agent_instances = {
            "StudyAgent": StudyAgent(self.db),
            "PlannerAgent": PlannerAgent(self.db),
            "AssignmentAgent": AssignmentAgent(self.db),
            "GoalAgent": GoalAgent(self.db),
            "ProgressAgent": ProgressAgent(self.db),
            "TutorAgent": TutorAgent(self.db),
            "QuizAgent": QuizAgent(self.db),
            "HabitAgent": HabitAgent(self.db),
            "RecommendationAgent": RecommendationAgent(self.db),
        }
        
        replies = []
        action_payload = None
        data_sources = []
        
        # Run the primary agent (or the first selected agent)
        primary_agent_name = agents_used[0] if agents_used else "TutorAgent"
        primary_agent = agent_instances.get(primary_agent_name, agent_instances["TutorAgent"])
        
        try:
            agent_res = primary_agent.run(student_id, query, context)
            replies.append(agent_res.get("answer", ""))
            action_payload = agent_res.get("action")
            data_sources = agent_res.get("data_sources", [])
        except Exception as e:
            logger.error(f"Error executing agent {primary_agent_name}: {e}")
            replies.append("Sorry, the specialist agent encountered an error processing your request.")
            
        final_answer = "\n".join(replies)
        
        # Standardized Response Format
        return {
            "answer": final_answer,
            "response_type": "text",
            "intent": intent,
            "agents_used": agents_used,
            "tools_used": tools_used,
            "memory_used": [m["content"] for m in context.get("memories", [])[-3:]],  # show recent memories
            "data_sources": data_sources,
            "requires_confirmation": routing.get("requires_confirmation", False),
            "action": action_payload
        }

    def process_and_execute(self, child_id: int, query: str) -> Dict[str, Any]:
        """
        Coordinates the specialized agents from specialized_agents.py.
        Used by tests and TwoWayWhatsAppParentAssistant.
        """
        from app.ai.context_builder import ChildContextBuilder
        from app.agents.specialized_agents import (
            EducationAgent, StudyCoachAgent, ExamPlannerAgent,
            WellnessAgent, ScreenTimeAgent, FinanceAgent,
            SafetyAgent, ActivityAgent, ParentCommunicationAgent
        )
        from app.models.homework import Homework
        from app.models.screen_time import ScreenTimeLog
        from datetime import date

        # 1. Build context
        builder = ChildContextBuilder(self.db, child_id)
        context = builder.build(include_ml_predictions=False)

        # 2. Select agents (supporting deterministic rules for tests & LLM fallbacks)
        query_lower = query.lower()
        selected_agents = []

        if "exam" in query_lower or "test" in query_lower:
            selected_agents = ["ExamPlannerAgent", "StudyCoachAgent", "EducationAgent"]
        elif "phone" in query_lower or "screen" in query_lower:
            selected_agents = ["ScreenTimeAgent", "EducationAgent", "ParentCommunicationAgent"]
        elif "afford" in query_lower or "price" in query_lower or "₹" in query_lower or "cost" in query_lower:
            selected_agents = ["FinanceAgent"]
        elif "stressed" in query_lower or "anxious" in query_lower or "sad" in query_lower:
            selected_agents = ["WellnessAgent", "StudyCoachAgent"]
        else:
            # Fallback to general LLM routing
            routing = self.select_agents_and_tools(query, context.profile.model_dump())
            agents_map = {
                "EducationAgent": "EducationAgent",
                "StudyCoachAgent": "StudyCoachAgent",
                "ExamPlannerAgent": "ExamPlannerAgent",
                "WellnessAgent": "WellnessAgent",
                "ScreenTimeAgent": "ScreenTimeAgent",
                "FinanceAgent": "FinanceAgent",
                "SafetyAgent": "SafetyAgent",
                "ActivityAgent": "ActivityAgent",
                "ParentCommunicationAgent": "ParentCommunicationAgent"
            }
            selected_agents = [agents_map[a] for a in routing.get("agents_used", []) if a in agents_map]
            if not selected_agents:
                selected_agents = ["EducationAgent"]

        # 3. Instantiate and run selected agents
        agent_instances = {
            "EducationAgent": EducationAgent(),
            "StudyCoachAgent": StudyCoachAgent(),
            "ExamPlannerAgent": ExamPlannerAgent(),
            "WellnessAgent": WellnessAgent(),
            "ScreenTimeAgent": ScreenTimeAgent(),
            "FinanceAgent": FinanceAgent(),
            "SafetyAgent": SafetyAgent(),
            "ActivityAgent": ActivityAgent(),
            "ParentCommunicationAgent": ParentCommunicationAgent()
        }

        execution_logs = []
        replies = []
        action_plan = []

        for name in selected_agents:
            agent = agent_instances.get(name)
            if agent:
                try:
                    res = agent.execute(self.db, child_id, query, context)
                    status = "SUCCESS"
                    reply_text = res.get("reply", "")
                    if not reply_text and "answer" in res:
                        reply_text = res["answer"]
                    
                    execution_logs.append({
                        "agent": name,
                        "status": status,
                        "reply": reply_text
                    })
                    replies.append(reply_text)

                    # Accumulate action recommendations
                    actions = res.get("actions", {})
                    if isinstance(actions, dict):
                        for k, v in actions.items():
                            action_plan.append(f"{name}: {k} - {v}")
                except Exception as e:
                    logger.error(f"Error running specialized agent {name}: {e}")
                    execution_logs.append({
                        "agent": name,
                        "status": "FAILED",
                        "reply": str(e)
                    })

        # 4. Conflict detection (e.g. high screen time and pending assignments)
        detected_conflicts = []
        pending_hw_count = context.homework.pending_count
        screen_mins = context.screen_time.avg_daily_minutes
        if pending_hw_count > 0 and screen_mins > 120.0:
            conflict_msg = (
                f"Conflict: The child spent {screen_mins} minutes of daily screen time "
                f"but has {pending_hw_count} pending homework assignment(s)."
            )
            detected_conflicts.append(conflict_msg)

        combined_reply = "\n".join(replies) if replies else "Processed successfully."

        return {
            "selected_agents": selected_agents,
            "execution_logs": execution_logs,
            "combined_reply": combined_reply,
            "detected_conflicts": detected_conflicts,
            "action_plan": action_plan
        }

