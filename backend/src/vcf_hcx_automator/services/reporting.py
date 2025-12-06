from typing import List
from vcf_hcx_automator.models import (
    ValidationReport, ValidationResult, ValidationError, RemediationSuggestion, ValidationSeverity
)

class ValidationReportGenerator:
    """Generate detailed validation reports"""
    
    def generate_validation_report(self, validation_results: List[ValidationResult]) -> ValidationReport:
        """Generate comprehensive validation report"""
        passed = sum(1 for r in validation_results if r.is_valid)
        failed = sum(1 for r in validation_results if not r.is_valid)
        critical = sum(1 for r in validation_results for e in r.errors if e.severity == ValidationSeverity.CRITICAL)
        warnings = sum(1 for r in validation_results for w in r.warnings)
        
        all_errors = [e for r in validation_results for e in r.errors]
        recommendations = self.generate_remediation_suggestions(all_errors)
        
        return ValidationReport(
            summary=f"Validation complete. {passed} passed, {failed} failed.",
            total_checks=len(validation_results),
            passed_checks=passed,
            failed_checks=failed,
            critical_errors=critical,
            warnings=warnings,
            results=validation_results,
            recommendations=recommendations
        )
    
    def generate_remediation_suggestions(self, validation_errors: List[ValidationError]) -> List[RemediationSuggestion]:
        """Generate remediation suggestions for validation errors"""
        suggestions = []
        seen_codes = set()
        
        for error in validation_errors:
            if error.code in seen_codes:
                continue
            
            if error.remediation:
                suggestions.append(error.remediation)
                seen_codes.add(error.code)
            elif error.code == "VM_NOT_FOUND":
                suggestions.append(RemediationSuggestion(
                    description="Ensure the VM exists in the source vCenter and the inventory cache is up to date.",
                    action_type="PROCESS",
                    steps=["Run 'inventory discover --refresh-cache'", "Verify VM name in CSV"]
                ))
                seen_codes.add(error.code)
            # Add more specific suggestions based on error codes
            
        return suggestions
    
    def format_validation_summary(self, report: ValidationReport) -> str:
        """Format validation summary for display"""
        return (
            f"Validation Report Summary:\n"
            f"--------------------------\n"
            f"Total Checks: {report.total_checks}\n"
            f"Passed: {report.passed_checks}\n"
            f"Failed: {report.failed_checks}\n"
            f"Critical Errors: {report.critical_errors}\n"
            f"Warnings: {report.warnings}\n"
        )
    
    def export_validation_report(self, report: ValidationReport, format: str) -> str:
        """Export validation report in specified format"""
        if format.lower() == "json":
            return report.model_dump_json(indent=2)
        # Add other formats like YAML or CSV if needed
        return self.format_validation_summary(report)
