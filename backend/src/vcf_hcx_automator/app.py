"""Main Litestar application for VCF HCX Automator."""

from litestar import Litestar, get, post
from litestar.config.cors import CORSConfig
from typing import List, Optional

from .config import settings
from .models import HCXMigrationRequest, HCXMigrationStatus, HCXSiteInfo
from .services import HCXService


@get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "service": "vcf-hcx-automator"}


@get("/sites", sync_to_thread=False)
async def get_sites() -> List[HCXSiteInfo]:
    """Get list of HCX sites."""
    service = HCXService()
    try:
        authenticated = await service.authenticate()
        if not authenticated:
            return []
        return await service.get_sites()
    finally:
        await service.close()


@post("/migrations", sync_to_thread=False)
async def create_migration(data: HCXMigrationRequest) -> Optional[HCXMigrationStatus]:
    """Create a new HCX migration."""
    service = HCXService()
    try:
        authenticated = await service.authenticate()
        if not authenticated:
            return None
        return await service.create_migration(data)
    finally:
        await service.close()


@get("/migrations/{migration_id:str}", sync_to_thread=False)
async def get_migration_status(migration_id: str) -> Optional[HCXMigrationStatus]:
    """Get status of a specific migration."""
    service = HCXService()
    try:
        authenticated = await service.authenticate()
        if not authenticated:
            return None
        return await service.get_migration_status(migration_id)
    finally:
        await service.close()


# Configure CORS
cors_config = CORSConfig(
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Create the Litestar application
app = Litestar(
    route_handlers=[
        health_check,
        get_sites,
        create_migration,
        get_migration_status,
    ],
    cors_config=cors_config,
    debug=settings.debug,
)