import httpx
import asyncio
import logging

logger = logging.getLogger(__name__)

async def send_agent_notification(url: str, payload: dict, retries: int = 3, timeout: float = 5.0) -> bool:
    logger.info(f"Sending outgoing message to agent endpoint: {url} | Payload: {payload}")
    
    for attempt in range(1, retries + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, json=payload)
                
                # Check for success (200 OK or 201 Created)
                if response.status_code in [200, 201]:
                    logger.info(f"Successfully delivered notification to {url} (Attempt {attempt}). Response status: {response.status_code}")
                    return True
                else:
                    logger.warning(f"Failed response from {url} (Attempt {attempt}). Status: {response.status_code} | Response: {response.text}")
                    
        except httpx.RequestError as e:
            logger.warning(f"Request connection error on attempt {attempt} to {url}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during notification on attempt {attempt} to {url}: {e}")
            
        # Backoff before retrying
        if attempt < retries:
            backoff_delay = attempt * 1.0
            logger.info(f"Retrying notification to {url} in {backoff_delay} seconds...")
            await asyncio.sleep(backoff_delay)
            
    logger.error(f"Failed to deliver notification to {url} after {retries} attempts.")
    return False
