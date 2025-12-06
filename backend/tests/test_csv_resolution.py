import pytest
from unittest.mock import AsyncMock, MagicMock
from vcf_hcx_automator.services.csv_resolution import CSVResolutionService
from vcf_hcx_automator.services.csv_parser import CSVParserService
from vcf_hcx_automator.services.resolution import NameResolutionService
from vcf_hcx_automator.services.inventory import InventoryDiscoveryService
from vcf_hcx_automator.models.csv import CSVParseResult, EnhancedMigrationCSVRow
from vcf_hcx_automator.models.inventory import VCenterVM, VCenterNetwork, VCenterDatastore, VCenterCluster

@pytest.fixture
def mock_parser():
    return AsyncMock(spec=CSVParserService)

@pytest.fixture
def mock_resolver():
    return AsyncMock(spec=NameResolutionService)

@pytest.fixture
def mock_inventory():
    return AsyncMock(spec=InventoryDiscoveryService)

@pytest.fixture
def resolution_service(mock_parser, mock_resolver):
    return CSVResolutionService(mock_parser, mock_resolver)

@pytest.mark.asyncio
async def test_resolve_csv_rows(resolution_service, mock_resolver, mock_inventory):
    # Setup
    rows = [
        EnhancedMigrationCSVRow(
            vm_name="vm1",
            source_network="net1", target_network="net2",
            source_datastore="ds1", target_datastore="ds2",
            source_compute="comp1", target_compute="comp2",
            row_number=2
        )
    ]
    
    mock_resolver.resolve_vm_by_name.return_value = VCenterVM(
        id="vm-1", name="vm1", type="VirtualMachine", power_state="poweredOn",
        cpu_count=2, memory_mb=4096, guest_os="ubuntu"
    )
    mock_resolver.resolve_network_by_name.return_value = VCenterNetwork(
        id="net-2", name="net2", type="Network", network_type="DistributedVirtualPortgroup"
    )
    mock_resolver.resolve_datastore_by_name.return_value = VCenterDatastore(
        id="ds-2", name="ds2", type="Datastore", capacity=100, free_space=50, type_info="VMFS"
    )
    mock_resolver.resolve_compute_by_name.return_value = VCenterCluster(
        id="comp-2", name="comp2", type="ClusterComputeResource"
    )
    
    # Execute
    resolved = await resolution_service.resolve_csv_rows(rows, mock_inventory)
    
    # Verify
    assert len(resolved) == 1
    assert resolved[0].vm_id == "vm-1"
    assert resolved[0].target_network_id == "net-2"
    assert resolved[0].target_datastore_id == "ds-2"
    assert resolved[0].target_compute_id == "comp-2"
    assert resolved[0].is_resolved

@pytest.mark.asyncio
async def test_resolve_csv_rows_missing_vm(resolution_service, mock_resolver, mock_inventory):
    rows = [
        EnhancedMigrationCSVRow(
            vm_name="vm1",
            source_network="net1", target_network="net2",
            source_datastore="ds1", target_datastore="ds2",
            source_compute="comp1", target_compute="comp2",
            row_number=2
        )
    ]
    
    mock_resolver.resolve_vm_by_name.return_value = None
    # Mock others to return something so only VM fails
    mock_resolver.resolve_network_by_name.return_value = VCenterNetwork(
        id="net-2", name="net2", type="Network", network_type="DistributedVirtualPortgroup"
    )
    mock_resolver.resolve_datastore_by_name.return_value = VCenterDatastore(
        id="ds-2", name="ds2", type="Datastore", capacity=100, free_space=50, type_info="VMFS"
    )
    mock_resolver.resolve_compute_by_name.return_value = VCenterCluster(
        id="comp-2", name="comp2", type="ClusterComputeResource"
    )

    resolved = await resolution_service.resolve_csv_rows(rows, mock_inventory)
    
    assert not resolved[0].is_resolved
    assert "VM 'vm1' not found" in resolved[0].resolution_errors

@pytest.mark.asyncio
async def test_group_rows_by_mobility_group(resolution_service):
    rows = [
        EnhancedMigrationCSVRow(
            vm_name="vm1", target_compute="comp1", migration_type="vmotion",
            source_network="s", target_network="t", source_datastore="s", target_datastore="t", source_compute="s", row_number=1,
            vm_id="1", target_network_id="1", target_datastore_id="1", target_compute_id="1"
        ),
        EnhancedMigrationCSVRow(
            vm_name="vm2", target_compute="comp1", migration_type="vmotion",
            source_network="s", target_network="t", source_datastore="s", target_datastore="t", source_compute="s", row_number=2,
            vm_id="2", target_network_id="1", target_datastore_id="1", target_compute_id="1"
        ),
        EnhancedMigrationCSVRow(
            vm_name="vm3", target_compute="comp2", migration_type="bulk",
            source_network="s", target_network="t", source_datastore="s", target_datastore="t", source_compute="s", row_number=3,
            vm_id="3", target_network_id="1", target_datastore_id="1", target_compute_id="1"
        )
    ]
    
    groups = resolution_service.group_rows_by_mobility_group(rows)
    assert len(groups) == 2
    assert "comp1_vmotion" in groups
    assert "comp2_bulk" in groups
    assert len(groups["comp1_vmotion"]) == 2
