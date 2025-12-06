import pytest
from vcf_hcx_automator.services.migration_group import MigrationGroupOrganizationService
from vcf_hcx_automator.models.csv import EnhancedMigrationCSVRow

@pytest.fixture
def group_service():
    return MigrationGroupOrganizationService()

def test_organize_mobility_groups(group_service):
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
        )
    ]
    
    groups = group_service.organize_mobility_groups(rows)
    assert len(groups) == 1
    assert groups[0].name == "comp1_vmotion"
    assert len(groups[0].vms) == 2
    assert groups[0].is_valid

def test_organize_mobility_groups_max_size(group_service):
    # Create 60 rows
    rows = []
    for i in range(60):
        rows.append(EnhancedMigrationCSVRow(
            vm_name=f"vm{i}", target_compute="comp1", migration_type="vmotion",
            source_network="s", target_network="t", source_datastore="s", target_datastore="t", source_compute="s", row_number=i,
            vm_id=f"{i}", target_network_id="1", target_datastore_id="1", target_compute_id="1"
        ))
        
    groups = group_service.organize_mobility_groups(rows)
    assert len(groups) == 2
    assert groups[0].name == "comp1_vmotion_1"
    assert len(groups[0].vms) == 50
    assert groups[1].name == "comp1_vmotion_2"
    assert len(groups[1].vms) == 10

def test_validate_mobility_group_empty(group_service):
    from vcf_hcx_automator.models.csv import MobilityGroupDefinition
    group = MobilityGroupDefinition(name="empty", vms=[], migration_type="vmotion")
    errors = group_service.validate_mobility_group(group)
    assert len(errors) == 1
    assert "Group is empty" in errors[0].message

def test_generate_group_recommendations(group_service):
    from vcf_hcx_automator.models.csv import MobilityGroupDefinition
    
    # Small group
    rows = [EnhancedMigrationCSVRow(
            vm_name="vm1", target_compute="comp1", migration_type="vmotion",
            source_network="s", target_network="t", source_datastore="s", target_datastore="t", source_compute="s", row_number=1,
            vm_id="1", target_network_id="1", target_datastore_id="1", target_compute_id="1"
    )]
    group = MobilityGroupDefinition(name="small", vms=rows, migration_type="vmotion")
    
    recs = group_service.generate_group_recommendations([group])
    assert len(recs) == 1
    assert "Group is very small" in recs[0].message
