import csv
import io
import chardet
from typing import List, Dict, Optional, TextIO, Union
from pathlib import Path
from ..models.csv import (
    CSVParseResult, CSVPreview, CSVStructureError, CSVFormat, CSVRowError
)
from .csv_validation import CSVValidationService

class CSVParserService:
    """Comprehensive CSV parsing with validation"""
    
    def __init__(self, validation_service: CSVValidationService):
        self.validation = validation_service
    
    async def parse_csv_file(self, file_path: str) -> CSVParseResult:
        """Parse CSV file with comprehensive validation"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")
            
        format_type = self.detect_csv_format(file_path)
        encoding = self._detect_encoding(file_path)
        
        try:
            with open(path, 'r', encoding=encoding, newline='') as f:
                return self._parse_csv_content(f, format_type)
        except Exception as e:
            return CSVParseResult(
                success=False,
                structure_errors=[CSVStructureError(
                    line_number=0,
                    message=f"Failed to read file: {str(e)}",
                    context="File Open"
                )]
            )
    
    async def parse_csv_data(self, csv_data: str) -> CSVParseResult:
        """Parse CSV data from string"""
        f = io.StringIO(csv_data)
        return self._parse_csv_content(f, CSVFormat.STANDARD)
    
    def _parse_csv_content(self, f: TextIO, format_type: CSVFormat) -> CSVParseResult:
        """Internal method to parse CSV content"""
        result = CSVParseResult(success=True, format=format_type)
        
        delimiter = ','
        if format_type == CSVFormat.TAB_DELIMITED:
            delimiter = '\t'
            
        try:
            # Read first few lines to validate structure
            sample = f.read(1024)
            f.seek(0)
            
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=[delimiter])
            except csv.Error:
                # Fallback to default dialect if sniffing fails
                dialect = csv.excel
                dialect.delimiter = delimiter

            reader = csv.DictReader(f, dialect=dialect)
            
            # Validate headers
            if reader.fieldnames:
                result.headers = list(reader.fieldnames)
                header_errors = self.validation.validate_csv_headers(result.headers)
                if header_errors:
                    result.header_errors = header_errors
                    result.success = False
            else:
                result.structure_errors.append(CSVStructureError(
                    line_number=1,
                    message="CSV file is empty or missing headers",
                    context="Header Check"
                ))
                result.success = False
                return result

            # Parse rows
            rows = []
            row_errors = []
            duplicates = []
            
            for i, row in enumerate(reader):
                # Clean whitespace from keys and values
                clean_row = {k.strip(): v.strip() for k, v in row.items() if k}
                rows.append(clean_row)
                
                # Validate row content
                r_errors = self.validation.validate_csv_row(clean_row, i + 2)
                if r_errors:
                    row_errors.extend(r_errors)
            
            result.rows = rows
            result.row_errors = row_errors
            
            # Check for duplicates
            duplicates = self.validation.check_duplicate_vms(rows)
            if duplicates:
                for dup in duplicates:
                    for row_num in dup.row_numbers:
                        result.row_errors.append(CSVRowError(
                            row_number=row_num,
                            column="vm_name",
                            value=dup.vm_name,
                            message=dup.message
                        ))

            if result.row_errors or result.header_errors or result.structure_errors:
                result.success = False
                
        except csv.Error as e:
            result.structure_errors.append(CSVStructureError(
                line_number=0,
                message=f"CSV parsing error: {str(e)}",
                context="CSV Parsing"
            ))
            result.success = False
            
        return result

    def validate_csv_structure(self, csv_reader) -> List[CSVStructureError]:
        """Validate CSV structure and headers"""
        # This is largely handled in _parse_csv_content but exposed here if needed separately
        # For now, we'll return empty as it's integrated
        return []

    def detect_csv_format(self, file_path: str) -> CSVFormat:
        """Auto-detect CSV format (delimiter, encoding, etc.)"""
        path = Path(file_path)
        if path.suffix.lower() in ['.tsv', '.txt']:
            return CSVFormat.TAB_DELIMITED
        return CSVFormat.STANDARD

    def _detect_encoding(self, file_path: str) -> str:
        """Detect file encoding"""
        with open(file_path, 'rb') as f:
            raw = f.read(1024)
            result = chardet.detect(raw)
            return result['encoding'] or 'utf-8'

    async def get_csv_preview(self, file_path: str, max_rows: int = 10) -> CSVPreview:
        """Get preview of CSV file for validation"""
        result = await self.parse_csv_file(file_path)
        
        return CSVPreview(
            headers=result.headers,
            rows=result.rows[:max_rows],
            total_rows=len(result.rows),
            format=result.format
        )
