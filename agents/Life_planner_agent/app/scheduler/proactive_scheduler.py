import logging
from apscheduler.schedulers.background import BackgroundScheduler
from app.database.session import SessionLocal
from app.ai.proactive_agent import proactive_agent

logger = logging.getLogger("kinnest.scheduler.proactive")

class ProactiveScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self._is_running = False

    def trigger_proactive_analysis_job(self):
        logger.info("[SCHEDULER JOB] Triggering periodic proactive AI life planner analysis")
        db = SessionLocal()
        try:
            # Invokes AI Proactive Planner agent purely to gather state & reason over facts
            result = proactive_agent.analyze_proactive_context(
                db=db,
                family_id="default_family",
                lookahead_days=30
            )
            logger.info(f"[SCHEDULER JOB] Completed proactive AI analysis. Insights generated: {len(result.insights)}")
        except Exception as exc:
            logger.error(f"[SCHEDULER JOB] Proactive AI analysis failed: {exc}")
        finally:
            db.close()

    def start(self, interval_hours: int = 12):
        if not self._is_running:
            self.scheduler.add_job(
                self.trigger_proactive_analysis_job,
                'interval',
                hours=interval_hours,
                id='proactive_ai_planner_job',
                replace_existing=True
            )
            self.scheduler.start()
            self._is_running = True
            logger.info(f"Proactive AI Scheduler started (interval: {interval_hours} hours)")

    def shutdown(self):
        if self._is_running:
            self.scheduler.shutdown()
            self._is_running = False
            logger.info("Proactive AI Scheduler shut down")

proactive_scheduler = ProactiveScheduler()
