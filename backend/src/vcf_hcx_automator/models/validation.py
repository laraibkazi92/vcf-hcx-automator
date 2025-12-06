from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import Field
from .base import BaseDataModel

class ValidationSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class RemediationSuggestion(BaseDataModel):
    description: str
    action_type: str  # e.g., "CONFIGURATION", "RESOURCE", "PROCESS"
    steps: List[str] = Field(default_factory=list)

class ValidationError(BaseDataModel):
    code: str
    message: str
    severity: ValidationSeverity
    resource_id: Optional[str] = None
    resource_type: Optional[str] = None
    remediation: Optional[RemediationSuggestion] = None

class ValidationResult(BaseDataModel):
    is_valid: bool
    errors: List[ValidationError] = Field(default_factory=list)
    warnings: List[ValidationError] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class VMValidationResult(ValidationResult):
    vm_id: str
    checks_passed: List[str] = Field(default_factory=list)
    checks_failed: List[str] = Field(default_factory=list)

class NetworkValidationResult(ValidationResult):
    vm_id: str
    network_id: str
    
class StorageValidationResult(ValidationResult):
    vm_id: str
    datastore_id: str

class ValidationReport(BaseDataModel):
    summary: str
    total_checks: int
    passed_checks: int
    failed_checks: int
    critical_errors: int
    warnings: int
    results: List[ValidationResult] = Field(default_factory=list)
    recommendations: List[RemediationSuggestion] = Field(default_factory=list)

class CompatibilityResult(BaseDataModel):
    is_compatible: bool
    reason: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    details: Dict[str, Any] = Field(default_factory=dict)

class HardwareCompatibilityResult(CompatibilityResult):
    cpu_compatible: bool = True
    memory_compatible: bool = True

class NetworkCompatibilityResult(CompatibilityResult):
    subnet_match: bool = True
    vlan_match: bool = True

class StorageCompatibilityResult(CompatibilityResult):
    capacity_sufficient: bool = True
    type_compatible: bool = True

class SoftwareCompatibilityResult(CompatibilityResult):
    tools_status: str = "UNKNOWN"
    os_supported: bool = True

class CompatibilityReport(BaseDataModel):
    vm_id: str
    target_site_id: str
    hardware: Optional[HardwareCompatibilityResult] = None
    network: Optional[NetworkCompatibilityResult] = None
    storage: Optional[StorageCompatibilityResult] = None
    software: Optional[SoftwareCompatibilityResult] = None
    overall_compatible: bool

class MigrationContext(BaseDataModel):
    mobility_group_id: str
    migration_id: Optional[str] = None
    current_state: str
    resources_affected: List[str] = Field(default_factory=list)

class RecoveryResult(BaseDataModel):
    success: bool
    message: str
    recovered_resources: List[str] = Field(default_factory=list)
    failed_resources: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)

class RollbackResult(BaseDataModel):
    success: bool
    message: str
    rollback_point: str
    
class CleanupResult(BaseDataModel):
    success: bool
    cleaned_resources: List[str] = Field(default_factory=list)
    pending_resources: List[str] = Field(default_factory=list)

class RecoveryPlan(BaseDataModel):
    error_type: str
    recommended_action: str
    steps: List[str] = Field(default_factory=list)
    estimated_time_seconds: int
