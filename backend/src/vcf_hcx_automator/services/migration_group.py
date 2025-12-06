from typing import List, Dict, Any
from ..models.csv import (
    EnhancedMigrationCSVRow, MobilityGroupDefinition, MobilityGroupError,
    GroupRecommendation
)

class MigrationGroupOrganizationService:
    """Organize CSV data into mobility groups"""
    
    MAX_VMS_PER_GROUP = 50
    
    def organize_mobility_groups(self, resolved_rows: List[EnhancedMigrationCSVRow]) -> List[MobilityGroupDefinition]:
        """Organize resolved rows into mobility group definitions"""
        groups = {}
        
        # Group by schedule_group or target_compute + migration_type
        for row in resolved_rows:
            if not row.is_valid or not row.is_resolved:
                continue
                
            if row.schedule_group:
                group_name = row.schedule_group
            else:
                group_name = f"{row.target_compute}_{row.migration_type}"
                
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(row)
            
        definitions = []
        for name, vms in groups.items():
            # Check if we need to split large groups
            if len(vms) > self.MAX_VMS_PER_GROUP:
                chunks = [vms[i:i + self.MAX_VMS_PER_GROUP] for i in range(0, len(vms), self.MAX_VMS_PER_GROUP)]
                for i, chunk in enumerate(chunks):
                    chunk_name = f"{name}_{i+1}"
                    definitions.append(self._create_group_definition(chunk_name, chunk))
            else:
                definitions.append(self._create_group_definition(name, vms))
                
        return definitions
    
    def _create_group_definition(self, name: str, vms: List[EnhancedMigrationCSVRow]) -> MobilityGroupDefinition:
        """Helper to create a group definition"""
        # Assume all VMs in a group share the same migration type if grouped automatically
        # If manually grouped, we might have mixed types which HCX might not support in one go depending on API
        # For now, take the most common type or just the first one
        mig_type = vms[0].migration_type if vms else "vmotion"
        
        definition = MobilityGroupDefinition(
            name=name,
            vms=vms,
            migration_type=mig_type
        )
        
        # Validate immediately
        definition.validation_errors = self.validate_mobility_group(definition)
        definition.recommendations = self.generate_group_recommendations([definition])
        
        return definition

    def validate_mobility_group(self, group: MobilityGroupDefinition) -> List[MobilityGroupError]:
        """Validate mobility group configuration"""
        errors = []
        
        if not group.vms:
            errors.append(MobilityGroupError(
                group_name=group.name,
                message="Group is empty"
            ))
            
        # Check for mixed migration types if that's a constraint (usually it is for a single wave)
        types = set(vm.migration_type for vm in group.vms)
        if len(types) > 1:
            errors.append(MobilityGroupError(
                group_name=group.name,
                message=f"Group contains mixed migration types: {', '.join(types)}. HCX typically requires uniform migration type per group."
            ))
            
        return errors
    
    def optimize_mobility_groups(self, groups: List[MobilityGroupDefinition]) -> List[MobilityGroupDefinition]:
        """Optimize mobility groups for better performance"""
        # Placeholder for more advanced optimization logic
        # e.g., balancing size, network locality, etc.
        return groups
    
    def generate_group_recommendations(self, groups: List[MobilityGroupDefinition]) -> List[GroupRecommendation]:
        """Generate recommendations for group optimization"""
        recommendations = []
        for group in groups:
            if len(group.vms) < 5:
                recommendations.append(GroupRecommendation(
                    group_name=group.name,
                    message="Group is very small. Consider merging with other groups for efficiency.",
                    impact="Low",
                    suggestion="Merge with similar groups targeting same destination."
                ))
            elif len(group.vms) == self.MAX_VMS_PER_GROUP:
                recommendations.append(GroupRecommendation(
                    group_name=group.name,
                    message="Group is at maximum capacity.",
                    impact="Medium",
                    suggestion="Ensure network bandwidth is sufficient for this batch size."
                ))
                
        return recommendations
