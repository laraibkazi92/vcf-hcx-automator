
from typing import List, Dict, Any, Optional
from ..models import (
    VMInventory, NetworkInventory, DatastoreInventory, ComputeInventory,
    EnhancedMigrationCSVRow, CSVResolutionResult, ResolutionReport,
    CSVParseResult, CSVRowError
)
from .csv_parser import CSVParserService
from .resolution import NameResolutionService
from .inventory import InventoryDiscoveryService

class CSVResolutionService:
    """CSV-to-inventory resolution with name-to-ID mapping"""
    
    def __init__(self, csv_parser: CSVParserService, name_resolver: NameResolutionService):
        self.csv_parser = csv_parser
        self.name_resolver = name_resolver
    
    async def resolve_csv_file(self, file_path: str, inventory_service: InventoryDiscoveryService) -> CSVResolutionResult:
        """Complete CSV file resolution pipeline"""
        # 1. Parse CSV
        parse_result = await self.csv_parser.parse_csv_file(file_path)
        if not parse_result.success:
            return CSVResolutionResult(
                total_rows=0,
                resolved_rows=0,
                failed_rows=0,
                rows=[],
                errors=[f"CSV Parsing failed: {e.message}" for e in parse_result.structure_errors]
            )
            
        # 2. Convert to Enhanced Rows
        enhanced_rows = []
        for i, row in enumerate(parse_result.rows):
            enhanced_rows.append(EnhancedMigrationCSVRow(
                vm_name=row.get("vm_name", ""),
                source_network=row.get("source_network", ""),
                target_network=row.get("target_network", ""),
                source_datastore=row.get("source_datastore", ""),
                target_datastore=row.get("target_datastore", ""),
                source_compute=row.get("source_compute", ""),
                target_compute=row.get("target_compute", ""),
                migration_type=row.get("migration_type", "vmotion"),
                schedule_group=row.get("schedule_group"),
                row_number=i + 2,
                validation_errors=[e for e in parse_result.row_errors if e.row_number == i + 2]
            ))
            
        # 3. Resolve Rows
        resolved_rows = await self.resolve_csv_rows(enhanced_rows, inventory_service)
        
        # 4. Group Rows
        groups = self.group_rows_by_mobility_group(resolved_rows)
        
        # 5. Calculate Stats
        total = len(resolved_rows)
        resolved_count = sum(1 for r in resolved_rows if r.is_resolved and r.is_valid)
        failed_count = total - resolved_count
        
        return CSVResolutionResult(
            total_rows=total,
            resolved_rows=resolved_count,
            failed_rows=failed_count,
            rows=resolved_rows,
            groups=groups
        )
    
    async def resolve_csv_rows(self, rows: List[EnhancedMigrationCSVRow], inventory_service: InventoryDiscoveryService) -> List[EnhancedMigrationCSVRow]:
        """Resolve CSV rows to inventory IDs"""
        # Ensure inventory is fresh or cached
        # We assume inventory_service has data or will fetch it
        
        resolved_rows = []
        for row in rows:
            if not row.is_valid:
                resolved_rows.append(row)
                continue
                
            resolved_row = await self.resolve_single_row(row, inventory_service)
            resolved_rows.append(resolved_row)
            
        return resolved_rows
    
    async def resolve_single_row(self, row: EnhancedMigrationCSVRow, inventory_service: InventoryDiscoveryService) -> EnhancedMigrationCSVRow:
        """Resolve single CSV row with detailed error handling"""
        # Resolve VM
        vm = await self.name_resolver.resolve_vm_by_name(row.vm_name)
        if vm:
            row.vm_id = vm.id
        else:
            row.resolution_errors.append(f"VM '{row.vm_name}' not found")
            
        # Resolve Target Network
        # Note: We might need to resolve source network too if needed for validation, but spec focuses on target mapping usually
        # Actually spec says "source_network" in CSV, so we should probably resolve it if we want to validate it exists
        # But for migration, target is critical.
        
        target_net = await self.name_resolver.resolve_network_by_name(row.target_network)
        if target_net:
            row.target_network_id = target_net.id
        else:
            row.resolution_errors.append(f"Target Network '{row.target_network}' not found")

        # Resolve Target Datastore
        target_ds = await self.name_resolver.resolve_datastore_by_name(row.target_datastore)
        if target_ds:
            row.target_datastore_id = target_ds.id
        else:
            row.resolution_errors.append(f"Target Datastore '{row.target_datastore}' not found")
            
        # Resolve Target Compute
        target_compute = await self.name_resolver.resolve_compute_by_name(row.target_compute)
        if target_compute:
            row.target_compute_id = target_compute.id
        else:
            row.resolution_errors.append(f"Target Compute '{row.target_compute}' not found")
            
        return row
    
    def group_rows_by_mobility_group(self, rows: List[EnhancedMigrationCSVRow]) -> Dict[str, List[EnhancedMigrationCSVRow]]:
        """Group resolved rows by mobility group"""
        groups = {}
        
        # Default grouping by schedule_group if present, otherwise by target_compute + migration_type
        # Or just put everything in "Default" if not specified.
        # Let's use schedule_group column first.
        
        for row in rows:
            if not row.is_valid or not row.is_resolved:
                group_name = "Unresolved/Invalid"
            elif row.schedule_group:
                group_name = row.schedule_group
            else:
                # Auto-group by target compute and migration type
                group_name = f"{row.target_compute}_{row.migration_type}"
                
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(row)
            
        return groups
    
    def generate_resolution_report(self, result: CSVResolutionResult) -> ResolutionReport:
        """Generate comprehensive resolution report"""
        common_errors = {}
        for row in result.rows:
            for error in row.resolution_errors:
                common_errors[error] = common_errors.get(error, 0) + 1
            for error in row.validation_errors:
                msg = error.message
                common_errors[msg] = common_errors.get(msg, 0) + 1
                
        recommendations = []
        if result.failed_rows > 0:
            recommendations.append("Check for typos in resource names")
            recommendations.append("Ensure all target resources exist in the destination environment")
            
        return ResolutionReport(
            summary=f"Resolved {result.resolved_rows}/{result.total_rows} VMs",
            total_vms=result.total_rows,
            resolved_vms=result.resolved_rows,
            unresolved_vms=result.failed_rows,
            groups_created=len(result.groups),
            common_errors=common_errors,
            recommendations=recommendations
        )
