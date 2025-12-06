"""Tests for VCF HCX Automator."""

import pytest
from unittest.mock import AsyncMock, patch

from vcf_hcx_automator.models import HCXMigrationRequest
from vcf_hcx_automator.services import HCXService


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    with patch("vcf_hcx_automator.services.settings") as mock:
        mock.vcf_host = "https://test-vcf.example.com"
        mock.vcf_username = "test_user"
        mock.vcf_password = "test_pass"
        mock.vcf_verify_ssl = False
        yield mock


@pytest.fixture
def hcx_service(mock_settings):
    """Create HCX service instance for testing."""
    return HCXService()


@pytest.mark.asyncio
async def test_authenticate_success(hcx_service):
    """Test successful authentication."""
    with patch.object(hcx_service.client, "post") as mock_post:
        mock_post.return_value.raise_for_status = AsyncMock()
        mock_post.return_value.json.return_value = {"token": "test_token"}
        
        result = await hcx_service.authenticate()
        assert result is True


@pytest.mark.asyncio
async def test_authenticate_failure(hcx_service):
    """Test authentication failure."""
    with patch.object(hcx_service.client, "post") as mock_post:
        mock_post.side_effect = Exception("Auth failed")
        
        result = await hcx_service.authenticate()
        assert result is False


@pytest.mark.asyncio
async def test_get_sites(hcx_service):
    """Test getting HCX sites."""
    mock_response = {
        "sites": [
            {
                "name": "site1",
                "type": "source",
                "status": "active",
                "endpoint_url": "https://site1.example.com"
            }
        ]
    }
    
    with patch.object(hcx_service, "authenticate", return_value=True), \
         patch.object(hcx_service.client, "get") as mock_get:
        mock_get.return_value.raise_for_status = AsyncMock()
        mock_get.return_value.json.return_value = mock_response
        
        sites = await hcx_service.get_sites()
        assert len(sites) == 1
        assert sites[0].name == "site1"
        assert sites[0].type == "source"


@pytest.mark.asyncio
async def test_create_migration(hcx_service):
    """Test creating a migration."""
    request = HCXMigrationRequest(
        source_site="site1",
        destination_site="site2",
        vm_names=["vm1", "vm2"],
        migration_type="v2v"
    )
    
    mock_response = {
        "migration_id": "mig-123",
        "created_at": "2024-01-01T00:00:00Z"
    }
    
    with patch.object(hcx_service, "authenticate", return_value=True), \
         patch.object(hcx_service.client, "post") as mock_post:
        mock_post.return_value.raise_for_status = AsyncMock()
        mock_post.return_value.json.return_value = mock_response
        
        migration = await hcx_service.create_migration(request)
        assert migration is not None
        assert migration.migration_id == "mig-123"
        assert migration.status == "pending"