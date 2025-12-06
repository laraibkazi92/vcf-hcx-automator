import pytest
from unittest.mock import AsyncMock, MagicMock
from vcf_hcx_automator.services.validation import PreMigrationValidationService, ResourceCompatibilityChecker
from vcf_hcx_automator.services.reporting import ValidationReportGenerator
from vcf_hcx_automator.services.recovery import ErrorRecoveryService
from vcf_hcx_automator.models import (
    VCenterVM, VCenterCluster, VCenterNetwork, VCenterDatastore,
    MobilityGroupDefinition, EnhancedMigrationCSVRow, ValidationSeverity,
    VMValidationResult, ValidationError
)

@pytest.fixture
def mock_inventory_service():
    service = AsyncMock()
    service.discover_vms.return_value = [
        VCenterVM(id="vm-1", name="test-vm", type="VirtualMachine", power_state="poweredOn", cpu_count=2, memory_mb=4096, guest_os="ubuntu64Guest"),
        VCenterVM(id="vm-2", name="test-vm-2", type="VirtualMachine", power_state="poweredOff", cpu_count=4, memory_mb=8192, guest_os="windows9Server64Guest")
    ]
    service.discover_compute_resources.return_value = [
        VCenterCluster(id="cluster-1", name="test-cluster", type="ClusterComputeResource")
    ]
    service.discover_networks.return_value = [
        VCenterNetwork(id="net-1", name="test-network", type="Network", network_type="Distributed")
    ]
    service.discover_datastores.return_value = [
        VCenterDatastore(id="ds-1", name="test-ds", type="Datastore", capacity=1000, free_space=500)
    ]
    return service

@pytest.fixture
def mock_compatibility_service():
    service = AsyncMock()
    service.check_vm_network_compatibility.return_value = MagicMock(is_compatible=True)
    service.check_vm_datastore_compatibility.return_value = MagicMock(is_compatible=True)
    return service

@pytest.mark.asyncio
async def test_resource_compatibility_checker(mock_inventory_service):
    checker = ResourceCompatibilityChecker(mock_inventory_service)
    
    # Test Hardware Compatibility
    res = await checker.check_vm_hardware_compatibility("vm-1", "cluster-1")
    assert res.is_compatible
    assert res.cpu_compatible
    
    res = await checker.check_vm_hardware_compatibility("vm-99", "cluster-1")
    assert not res.is_compatible
    assert "not found" in res.reason

@pytest.mark.asyncio
async def test_pre_migration_validation(mock_inventory_service, mock_compatibility_service):
    service = PreMigrationValidationService(mock_inventory_service, mock_compatibility_service)
    
    # Test VM Readiness
    res = await service.validate_vm_readiness("vm-1", None)
    assert res.is_valid
    assert "Power State Check" in res.checks_passed
    
    res = await service.validate_vm_readiness("vm-99", None)
    assert not res.is_valid
    assert res.errors[0].code == "VM_NOT_FOUND"

def test_validation_report_generator():
    generator = ValidationReportGenerator()
    
    results = [
        VMValidationResult(
            is_valid=True, 
            vm_id="vm-1", 
            checks_passed=["Check 1"], 
            checks_failed=[]
        ),
        VMValidationResult(
            is_valid=False, 
            vm_id="vm-2", 
            checks_passed=[], 
            checks_failed=["Check 2"],
            errors=[
                ValidationError(
                    code="TEST_ERROR", 
                    message="Test error", 
                    severity=ValidationSeverity.ERROR
                )
            ]
        )
    ]
    
    report = generator.generate_validation_report(results)
    assert report.total_checks == 2
    assert report.passed_checks == 1
    assert report.failed_checks == 1
    assert len(report.results) == 2

@pytest.mark.asyncio
async def test_error_recovery_service():
    service = ErrorRecoveryService()
    
    # Test Recovery Plan
    plan = service.generate_recovery_plan(ValueError("Test error"))
    assert plan.error_type == "ValueError"
    assert "Manual Intervention" in plan.recommended_action
