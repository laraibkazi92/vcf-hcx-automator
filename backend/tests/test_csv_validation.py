import pytest
from vcf_hcx_automator.services.csv_validation import CSVValidationService
from vcf_hcx_automator.models.csv import CSVHeaderError, CSVRowError, CSVValidationError, CSVDuplicateError

@pytest.fixture
def validation_service():
    return CSVValidationService()

def test_validate_csv_headers_valid(validation_service):
    headers = [
        "vm_name", "source_network", "target_network", 
        "source_datastore", "target_datastore", 
        "source_compute", "target_compute", "migration_type"
    ]
    errors = validation_service.validate_csv_headers(headers)
    assert len(errors) == 0

def test_validate_csv_headers_missing(validation_service):
    headers = ["vm_name", "source_network"]
    errors = validation_service.validate_csv_headers(headers)
    assert len(errors) == 1
    assert isinstance(errors[0], CSVHeaderError)
    assert "target_network" in errors[0].missing_headers

def test_validate_csv_row_valid(validation_service):
    row = {
        "vm_name": "vm1",
        "source_network": "net1",
        "target_network": "net2",
        "source_datastore": "ds1",
        "target_datastore": "ds2",
        "source_compute": "comp1",
        "target_compute": "comp2",
        "migration_type": "vmotion"
    }
    errors = validation_service.validate_csv_row(row, 1)
    assert len(errors) == 0

def test_validate_csv_row_missing_field(validation_service):
    row = {
        "vm_name": "vm1",
        "source_network": "", # Empty
        "target_network": "net2",
        "source_datastore": "ds1",
        "target_datastore": "ds2",
        "source_compute": "comp1",
        "target_compute": "comp2"
    }
    errors = validation_service.validate_csv_row(row, 1)
    assert len(errors) == 1
    assert errors[0].column == "source_network"

def test_validate_migration_type_invalid(validation_service):
    error = validation_service.validate_migration_type("invalid_type")
    assert error is not None
    assert error.field == "migration_type"

def test_check_duplicate_vms(validation_service):
    rows = [
        {"vm_name": "vm1"},
        {"vm_name": "vm2"},
        {"vm_name": "vm1"}
    ]
    duplicates = validation_service.check_duplicate_vms(rows)
    assert len(duplicates) == 1
    assert duplicates[0].vm_name == "vm1"
    assert len(duplicates[0].row_numbers) == 2
