import pytest
import os
from vcf_hcx_automator.services.csv_parser import CSVParserService
from vcf_hcx_automator.services.csv_validation import CSVValidationService
from vcf_hcx_automator.models.csv import CSVFormat

@pytest.fixture
def parser_service():
    validation = CSVValidationService()
    return CSVParserService(validation)

@pytest.mark.asyncio
async def test_parse_csv_data_valid(parser_service):
    csv_data = """vm_name,source_network,target_network,source_datastore,target_datastore,source_compute,target_compute
vm1,net1,net2,ds1,ds2,comp1,comp2"""
    result = await parser_service.parse_csv_data(csv_data)
    assert result.success
    assert len(result.rows) == 1
    assert result.rows[0]["vm_name"] == "vm1"

@pytest.mark.asyncio
async def test_parse_csv_data_invalid_header(parser_service):
    csv_data = """vm_name,source_network
vm1,net1"""
    result = await parser_service.parse_csv_data(csv_data)
    assert not result.success
    assert result.header_errors

@pytest.mark.asyncio
async def test_parse_csv_file(parser_service, tmp_path):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("""vm_name,source_network,target_network,source_datastore,target_datastore,source_compute,target_compute
vm1,net1,net2,ds1,ds2,comp1,comp2""")
    
    result = await parser_service.parse_csv_file(str(csv_file))
    assert result.success
    assert len(result.rows) == 1

@pytest.mark.asyncio
async def test_detect_csv_format(parser_service, tmp_path):
    csv_file = tmp_path / "test.csv"
    assert parser_service.detect_csv_format(str(csv_file)) == CSVFormat.STANDARD
    
    tsv_file = tmp_path / "test.tsv"
    assert parser_service.detect_csv_format(str(tsv_file)) == CSVFormat.TAB_DELIMITED
