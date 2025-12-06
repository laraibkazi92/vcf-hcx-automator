from typing import List, Optional, Dict, Any
from vcf_hcx_automator.services.base import BaseHTTPClient
from vcf_hcx_automator.config import settings
from vcf_hcx_automator.models import (
    HCXSiteSystem, HCXServiceMesh, HCXMobilityGroup,
    HCXMobilityGroupRequest, HCXValidationResult, HCXMigrationResult
)

class HCXClient(BaseHTTPClient):
    """HCX REST API client for migration operations"""

    def __init__(self):
        super().__init__(
            base_url=f"https://{settings.hcx_manager}/hybridity/api",
            verify_ssl=settings.hcx_verify_ssl
        )
        self.auth_token: Optional[str] = None

    async def authenticate(self) -> bool:
        """Authenticate with HCX and establish session"""
        try:
            response = await self.client.post(
                "/sessions",
                json={
                    "username": settings.hcx_username,
                    "password": settings.hcx_password
                }
            )
            response.raise_for_status()
            self.auth_token = response.headers.get("x-hm-authorization")
            if self.auth_token:
                self.client.headers["x-hm-authorization"] = self.auth_token
                return True
            return False
        except Exception as e:
            self.logger.error(f"HCX authentication failed: {str(e)}")
            return False

    async def get_site_systems(self) -> List[HCXSiteSystem]:
        """Get HCX site systems"""
        data = await self.get("/interconnect/site-systems")
        sites = []
        for item in data.get("items", []):
            sites.append(HCXSiteSystem(
                system_id=item.get("id"),
                name=item.get("name"),
                type=item.get("type", "unknown"),
                url=item.get("url", ""),
                state=item.get("state", "unknown"),
                version=item.get("version", "unknown")
            ))
        return sites

    async def get_service_meshes(self) -> List[HCXServiceMesh]:
        """Get HCX service meshes"""
        data = await self.get("/interconnect/service-meshes")
        meshes = []
        for item in data.get("items", []):
            meshes.append(HCXServiceMesh(
                mesh_id=item.get("id"),
                name=item.get("name"),
                source_site_id=item.get("sourceSiteId"),
                destination_site_id=item.get("destinationSiteId"),
                status=item.get("status", "unknown"),
                appliances=item.get("appliances", [])
            ))
        return meshes

    async def get_mobility_groups(self) -> List[HCXMobilityGroup]:
        """Get mobility groups"""
        data = await self.get("/mobility/mobility-groups")
        groups = []
        for item in data.get("items", []):
            groups.append(HCXMobilityGroup(
                group_id=item.get("id"),
                name=item.get("name"),
                source_site_id=item.get("sourceId"),
                destination_site_id=item.get("destinationId"),
                service_mesh_id=item.get("serviceMeshId"),
                migration_type=item.get("type"),
                state=item.get("state"),
                migrations=item.get("migrations", [])
            ))
        return groups

    async def create_mobility_group(self, group: HCXMobilityGroupRequest) -> HCXMobilityGroup:
        """Create new mobility group"""
        payload = group.model_dump(by_alias=True)
        data = await self.post("/mobility/mobility-groups", data=payload)
        return HCXMobilityGroup(
            group_id=data.get("id"),
            name=data.get("name"),
            source_site_id=data.get("sourceId"),
            destination_site_id=data.get("destinationId"),
            service_mesh_id=data.get("serviceMeshId"),
            migration_type=data.get("type"),
            state=data.get("state"),
            migrations=data.get("migrations", [])
        )

    async def update_mobility_group(self, group_id: str, group: HCXMobilityGroupRequest) -> HCXMobilityGroup:
        """Update existing mobility group"""
        payload = group.model_dump(by_alias=True)
        data = await self.put(f"/mobility/mobility-groups/{group_id}", data=payload)
        return HCXMobilityGroup(
            group_id=data.get("id"),
            name=data.get("name"),
            source_site_id=data.get("sourceId"),
            destination_site_id=data.get("destinationId"),
            service_mesh_id=data.get("serviceMeshId"),
            migration_type=data.get("type"),
            state=data.get("state"),
            migrations=data.get("migrations", [])
        )

    async def validate_mobility_group(self, group_id: str) -> HCXValidationResult:
        """Validate mobility group configuration"""
        data = await self.post(f"/mobility/mobility-groups/{group_id}/validate")
        return HCXValidationResult(
            is_valid=data.get("isValid", False),
            errors=data.get("errors", []),
            warnings=data.get("warnings", [])
        )

    async def start_migration(self, group_id: str) -> HCXMigrationResult:
        """Start mobility group migration"""
        data = await self.post(f"/mobility/mobility-groups/{group_id}/start")
        return HCXMigrationResult(
            migration_id=data.get("id"),
            status=data.get("state"),
            message="Migration started"
        )

    async def cancel_migration(self, group_id: str) -> HCXMigrationResult:
        """Cancel mobility group migration"""
        data = await self.post(f"/mobility/mobility-groups/{group_id}/cancel")
        return HCXMigrationResult(
            migration_id=data.get("id"),
            status=data.get("state"),
            message="Migration cancelled"
        )
