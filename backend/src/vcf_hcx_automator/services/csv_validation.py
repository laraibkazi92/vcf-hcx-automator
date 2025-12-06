from typing import List, Dict, Optional, Any
from ..models.csv import (
    CSVHeaderError, CSVRowError, CSVValidationError, CSVDuplicateError
)

class CSVValidationService:
    """CSV content validation and error detection"""
    
    REQUIRED_HEADERS = [
        "vm_name", "source_network", "target_network", 
        "source_datastore", "target_datastore", 
        "source_compute", "target_compute"
    ]
    
    VALID_MIGRATION_TYPES = ["vmotion", "bulk", "rav", "cold"]
    
    def validate_csv_headers(self, headers: List[str]) -> List[CSVHeaderError]:
        """Validate CSV headers against expected schema"""
        errors = []
        headers_lower = [h.lower().strip() for h in headers]
        
        missing = [h for h in self.REQUIRED_HEADERS if h not in headers_lower]
        unknown = [h for h in headers_lower if h not in self.REQUIRED_HEADERS and h != "migration_type" and h != "schedule_group"]
        
        if missing:
            errors.append(CSVHeaderError(
                missing_headers=missing,
                unknown_headers=unknown,
                message=f"Missing required headers: {', '.join(missing)}"
            ))
            
        return errors
    
    def validate_csv_row(self, row: Dict[str, str], row_number: int) -> List[CSVRowError]:
        """Validate individual CSV row"""
        errors = []
        
        # Check required fields
        for field in self.REQUIRED_HEADERS:
            if not row.get(field) or not row.get(field).strip():
                errors.append(CSVRowError(
                    row_number=row_number,
                    column=field,
                    value="",
                    message=f"Field '{field}' is required"
                ))
        
        # Validate migration type if present
        if "migration_type" in row and row["migration_type"]:
            mig_type = row["migration_type"].lower().strip()
            if mig_type not in self.VALID_MIGRATION_TYPES:
                errors.append(CSVRowError(
                    row_number=row_number,
                    column="migration_type",
                    value=mig_type,
                    message=f"Invalid migration type. Must be one of: {', '.join(self.VALID_MIGRATION_TYPES)}",
                    suggestion=self._suggest_migration_type(mig_type)
                ))
                
        return errors
    
    def validate_migration_type(self, migration_type: str) -> Optional[CSVValidationError]:
        """Validate migration type value"""
        if migration_type.lower().strip() not in self.VALID_MIGRATION_TYPES:
            return CSVValidationError(
                field="migration_type",
                value=migration_type,
                message=f"Invalid migration type. Must be one of: {', '.join(self.VALID_MIGRATION_TYPES)}"
            )
        return None
    
    def validate_boolean_field(self, field_value: str, field_name: str) -> Optional[CSVValidationError]:
        """Validate boolean field values"""
        valid_true = ['true', 'yes', '1', 'on']
        valid_false = ['false', 'no', '0', 'off']
        
        val = str(field_value).lower().strip()
        if val not in valid_true and val not in valid_false:
            return CSVValidationError(
                field=field_name,
                value=field_value,
                message=f"Invalid boolean value for '{field_name}'"
            )
        return None
    
    def check_duplicate_vms(self, rows: List[Dict[str, str]]) -> List[CSVDuplicateError]:
        """Check for duplicate VM entries"""
        vm_map = {}
        duplicates = []
        
        for i, row in enumerate(rows):
            vm_name = row.get("vm_name", "").strip()
            if vm_name:
                if vm_name in vm_map:
                    vm_map[vm_name].append(i + 2) # +2 for header and 1-based indexing
                else:
                    vm_map[vm_name] = [i + 2]
                    
        for vm_name, row_nums in vm_map.items():
            if len(row_nums) > 1:
                duplicates.append(CSVDuplicateError(
                    row_numbers=row_nums,
                    vm_name=vm_name,
                    message=f"Duplicate VM entry '{vm_name}' found on rows {', '.join(map(str, row_nums))}"
                ))
                
        return duplicates

    def _suggest_migration_type(self, invalid_type: str) -> Optional[str]:
        """Simple suggestion logic for typos"""
        # This could be enhanced with fuzzy matching later
        if "motion" in invalid_type:
            return "vmotion"
        return None
