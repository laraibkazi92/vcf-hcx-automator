import pytest
import os
from vcf_hcx_automator.config.settings import AppSettings
from vcf_hcx_automator.utils.logging import setup_logging
from vcf_hcx_automator.models.errors import ErrorResponse
from vcf_hcx_automator.services.base import BaseHTTPClient
from vcf_hcx_automator.utils.exceptions import APIError

@pytest.mark.asyncio
async def test_configuration_loading():
    """Test that configuration loads correctly"""
    # Set required env vars for testing
    os.environ["APP_VCENTER__HOST"] = "vc.example.com"
    os.environ["APP_VCENTER__USERNAME"] = "admin"
    os.environ["APP_VCENTER__PASSWORD"] = "password"
    os.environ["APP_HCX__MANAGER"] = "hcx.example.com"
    os.environ["APP_HCX__USERNAME"] = "admin"
    os.environ["APP_HCX__PASSWORD"] = "password"
    
    settings = AppSettings()
    assert settings.vcenter.host == "vc.example.com"
    assert settings.hcx.manager == "hcx.example.com"
    assert settings.app_name == "VCF HCX Automator"

def test_logging_setup():
    """Test logging configuration"""
    setup_logging(level="DEBUG", json_format=True)
    # No assertion, just checking it doesn't crash

def test_error_model():
    """Test error model creation"""
    error = ErrorResponse(
        code="TEST_ERROR",
        message="Test error message",
        details={"foo": "bar"}
    )
    assert error.code == "TEST_ERROR"
    assert error.details["foo"] == "bar"

import respx
from httpx import Response

@pytest.mark.asyncio
async def test_http_client():
    """Test HTTP client instantiation and basic usage (mocked)"""
    async with respx.mock:
        respx.get("https://mock.example.com/get").mock(return_value=Response(200, json={"args": {"test": "value"}}))
        
        client = BaseHTTPClient(base_url="https://mock.example.com")
        try:
            response = await client.get("/get", params={"test": "value"})
            assert response["args"]["test"] == "value"
        finally:
            await client.close()

@pytest.mark.asyncio
async def test_http_client_error():
    """Test HTTP client error handling"""
    async with respx.mock:
        respx.get("https://mock.example.com/status/404").mock(return_value=Response(404))
        
        client = BaseHTTPClient(base_url="https://mock.example.com")
        try:
            with pytest.raises(APIError) as excinfo:
                await client.get("/status/404")
            # 404 raises ResourceNotFoundError which is an APIError
            assert excinfo.value.details["status_code"] == 404
            assert "Resource not found" in str(excinfo.value)
        finally:
            await client.close()

