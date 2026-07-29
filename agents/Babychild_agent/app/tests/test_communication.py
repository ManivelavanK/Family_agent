import pytest
import httpx
from unittest.mock import patch, AsyncMock
from app.services import communication_service
from app.communication import agent_client

@pytest.mark.anyio
async def test_notify_mother_success():
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = httpx.Response(200)
        
        status = await communication_service.notify_mother_low_formula(101, 1)
        
    assert status is True
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert kwargs["json"]["item_name"] == "Baby Formula"

@pytest.mark.anyio
async def test_notify_father_success():
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = httpx.Response(201)
        
        status = await communication_service.notify_father_medical_expense(101, 1, "Vaccination", 1500, "Vaccine fee")
        
    assert status is True
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert kwargs["json"]["expense_type"] == "Vaccination"
    assert kwargs["json"]["amount"] == 1500

@pytest.mark.anyio
async def test_notify_grandparent_success():
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = httpx.Response(200)
        
        status = await communication_service.notify_grandparent_health_update(101, 1, "Baby John", "Fever detected", "Please check temperature.")
        
    assert status is True
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert kwargs["json"]["baby_name"] == "Baby John"
    assert kwargs["json"]["health_status"] == "Fever detected"

@pytest.mark.anyio
async def test_notify_planning_agent_success():
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = httpx.Response(200)
        
        status = await communication_service.notify_planning_agent(101, 1, "Vaccination", "BCG shot", "2026-08-15", "HIGH", "10:00 AM")
        
    assert status is True
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert kwargs["json"]["event_type"] == "Vaccination"
    assert kwargs["json"]["title"] == "BCG shot"

@pytest.mark.anyio
async def test_retry_behavior_on_temporary_failures():
    # If the first two requests throw connection error, and third succeeds
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post, \
         patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
         
        mock_post.side_effect = [
            httpx.RequestError("Connection timed out", request=None),
            httpx.RequestError("Temporary network issue", request=None),
            httpx.Response(200) # success
        ]
        
        status = await agent_client.send_agent_notification("http://test-agent", {}, retries=3)
        
    assert status is True
    assert mock_post.call_count == 3
    assert mock_sleep.call_count == 2

@pytest.mark.anyio
async def test_connection_failure():
    # If all retries fail
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post, \
         patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
         
        mock_post.side_effect = httpx.RequestError("Server offline", request=None)
        
        status = await agent_client.send_agent_notification("http://test-agent", {}, retries=3)
        
    assert status is False
    assert mock_post.call_count == 3
