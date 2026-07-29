import logging
from datetime import datetime
from backend.workflow.models import WorkflowInstance, WorkflowDefinition
from backend.workflow.state_machine import validate_transition
from backend.workflow.registry import registry
from backend.workflow.handlers import STEP_HANDLERS

logger = logging.getLogger("orchestrator.workflow.executor")

class WorkflowExecutor:
    @staticmethod
    async def execute_instance(instance: WorkflowInstance, blueprint: WorkflowDefinition):
        """Sequentially runs pending steps in a workflow instance using definition handlers."""
        if instance.status in ["COMPLETED", "CANCELLED"]:
            return

        # 1. Update status to RUNNING if currently PENDING or WAITING
        if instance.status in ["PENDING", "WAITING", "FAILED"]:
            if validate_transition(instance.status, "RUNNING"):
                registry.update_status(instance.workflow_id, "RUNNING")
            else:
                logger.warning(f"Invalid transition from {instance.status} to RUNNING for workflow {instance.workflow_id}")
                return

        steps = blueprint.steps
        
        while instance.current_step_index < len(steps):
            step = steps[instance.current_step_index]
            instance.step_states[step.name] = "RUNNING"
            instance.updated_time = datetime.utcnow()
            
            handler = STEP_HANDLERS.get(step.handler_name)
            if not handler:
                err_msg = f"Step handler '{step.handler_name}' not found for step '{step.name}'."
                logger.error(err_msg)
                instance.logs.append(err_msg)
                instance.step_states[step.name] = "FAILED"
                instance.failed_steps.append(step.name)
                registry.update_status(instance.workflow_id, "FAILED")
                return

            try:
                # Call definition-driven step handler
                result = await handler(instance.context_payload, instance.logs)
                
                if result == "SUCCESS":
                    instance.step_states[step.name] = "SUCCESS"
                    if step.name not in instance.completed_steps:
                        instance.completed_steps.append(step.name)
                    instance.current_step_index += 1
                    instance.logs.append(f"Step '{step.name}' executed successfully.")
                    
                elif result == "WAITING":
                    instance.step_states[step.name] = "WAITING"
                    registry.update_status(instance.workflow_id, "WAITING")
                    instance.logs.append(f"Step '{step.name}' entered WAITING state.")
                    return  # Stop executing; wait for background poller to resume
                    
                elif result == "FAILED":
                    instance.step_states[step.name] = "FAILED"
                    if step.name not in instance.failed_steps:
                        instance.failed_steps.append(step.name)
                        
                    # Check for retries
                    retries_count = instance.retries.get(step.name, 0)
                    if step.retryable and retries_count < step.max_retries:
                        instance.retries[step.name] = retries_count + 1
                        registry.update_status(instance.workflow_id, "WAITING")
                        instance.logs.append(f"Step '{step.name}' failed. Scheduling retry {retries_count + 1}/{step.max_retries}...")
                        return
                    else:
                        registry.update_status(instance.workflow_id, "FAILED")
                        instance.logs.append(f"Step '{step.name}' failed and max retries exceeded. Workflow marked FAILED.")
                        return
            except Exception as e:
                instance.step_states[step.name] = "FAILED"
                if step.name not in instance.failed_steps:
                    instance.failed_steps.append(step.name)
                    
                err_msg = f"Exception executing step '{step.name}': {e}"
                logger.error(err_msg, exc_info=True)
                instance.logs.append(err_msg)
                
                # Check for retries
                retries_count = instance.retries.get(step.name, 0)
                if step.retryable and retries_count < step.max_retries:
                    instance.retries[step.name] = retries_count + 1
                    registry.update_status(instance.workflow_id, "WAITING")
                    instance.logs.append(f"Scheduling retry {retries_count + 1}/{step.max_retries} due to exception...")
                    return
                else:
                    registry.update_status(instance.workflow_id, "FAILED")
                    return

        # 3. If all steps completed
        if instance.current_step_index == len(steps):
            registry.update_status(instance.workflow_id, "COMPLETED")
            instance.logs.append("Workflow completed successfully.")
