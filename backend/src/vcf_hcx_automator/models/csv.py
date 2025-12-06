from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum

class CSVFormat(str, Enum):
    """Supported CSV formats"""
    STANDARD = "standard"
    EXCEL = "excel"
    TAB_DELIMITED = "tab_delimited"

class CSVStructureError(BaseModel):
    """Error in CSV structure"""
    line_number: int
    message: str
    context: str

class CSVHeaderError(BaseModel):
    """Error in CSV headers"""
    missing_headers: List[str]
    unknown_headers: List[str]
    message: str

class CSVRowError(BaseModel):
    """Error in specific CSV row"""
    row_number: int
    column: str
    value: str
    message: str
    suggestion: Optional[str] = None

class CSVValidationError(BaseModel):
    """General CSV validation error"""
    field: str
    message: str
    value: Any

class CSVDuplicateError(BaseModel):
    """Duplicate entry error"""
    row_numbers: List[int]
    vm_name: str
    message: str

class CSVPreview(BaseModel):
    """Preview of CSV content"""
    headers: List[str]
    rows: List[Dict[str, str]]
    total_rows: int
    format: CSVFormat

class CSVParseResult(BaseModel):
    """Result of CSV parsing operation"""
    success: bool
    headers: List[str] = []
    rows: List[Dict[str, str]] = []
    structure_errors: List[CSVStructureError] = []
    header_errors: List[CSVHeaderError] = []
    row_errors: List[CSVRowError] = []
    format: CSVFormat = CSVFormat.STANDARD

class EnhancedMigrationCSVRow(BaseModel):
    """Enhanced CSV row with resolved IDs"""
    # Raw CSV Data
    vm_name: str
    source_network: str
    target_network: str
    source_datastore: str
    target_datastore: str
    source_compute: str
    target_compute: str
    migration_type: str = "vmotion"
    schedule_group: Optional[str] = None
    
    # Resolved IDs
    vm_id: Optional[str] = None
    source_network_id: Optional[str] = None
    target_network_id: Optional[str] = None
    source_datastore_id: Optional[str] = None
    target_datastore_id: Optional[str] = None
    source_compute_id: Optional[str] = None
    target_compute_id: Optional[str] = None
    
    # Metadata
    row_number: int
    validation_errors: List[CSVRowError] = []
    resolution_errors: List[str] = []
    
    @property
    def is_valid(self) -> bool:
        return not self.validation_errors
        
    @property
    def is_resolved(self) -> bool:
        return all([
            self.vm_id,
            self.target_network_id,
            self.target_datastore_id,
            self.target_compute_id
        ])

class MobilityGroupError(BaseModel):
    """Error in mobility group configuration"""
    group_name: str
    message: str
    severity: str = "error"

class GroupRecommendation(BaseModel):
    """Recommendation for group optimization"""
    group_name: str
    message: str
    impact: str
    suggestion: str

class MobilityGroupDefinition(BaseModel):
    """Definition of a mobility group"""
    name: str
    vms: List[EnhancedMigrationCSVRow]
    migration_type: str
    schedule_time: Optional[str] = None
    validation_errors: List[MobilityGroupError] = []
    recommendations: List[GroupRecommendation] = []
    
    @property
    def vm_count(self) -> int:
        return len(self.vms)
    
    @property
    def is_valid(self) -> bool:
        return not self.validation_errors and all(vm.is_valid and vm.is_resolved for vm in self.vms)

class CSVResolutionResult(BaseModel):
    """Result of CSV resolution process"""
    total_rows: int
    resolved_rows: int
    failed_rows: int
    rows: List[EnhancedMigrationCSVRow]
    groups: Dict[str, List[EnhancedMigrationCSVRow]] = {}
    errors: List[str] = []

class ResolutionReport(BaseModel):
    """Comprehensive resolution report"""
    summary: str
    total_vms: int
    resolved_vms: int
    unresolved_vms: int
    groups_created: int
    common_errors: Dict[str, int]
    recommendations: List[str]
