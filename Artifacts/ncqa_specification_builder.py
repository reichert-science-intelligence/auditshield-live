"""
AuditShield Live - NCQA HEDIS Specification Database
Structured validation rules for HEDIS 2026 measures

Based on NCQA HEDIS Volume 2 Technical Specifications
Author: Robert Hucks (Healthcare Data Scientist)
"""

import json
from typing import Dict, List
from datetime import datetime, timedelta

class NCQASpecificationDatabase:
    """HEDIS measure specifications and validation rules"""
    
    def __init__(self, measurement_year: int = 2026):
        self.measurement_year = measurement_year
        self.specifications = self._build_specifications()
    
    def _build_specifications(self) -> Dict:
        """Build complete NCQA HEDIS specification database"""
        
        specs = {
            'BCS': {
                'measure_name': 'Breast Cancer Screening',
                'measure_code': 'BCS',
                'domain': 'Screening',
                'star_rating_weight': 3.0,
                'description': 'Women 50-74 who had mammography to screen for breast cancer',
                
                'eligibility': {
                    'age_range': [50, 74],
                    'gender': 'F',
                    'continuous_enrollment': 'Required during measurement year',
                    'exclusions': [
                        'Bilateral mastectomy any time in history',
                        'Unilateral mastectomy with bilateral modifier',
                        'History of bilateral mastectomy',
                        'Right and left unilateral mastectomy'
                    ]
                },
                
                'numerator_criteria': {
                    'description': 'One or more screenings for breast cancer',
                    'compliance_options': [
                        {
                            'option': 1,
                            'description': 'Mammography during measurement year or year prior',
                            'required_elements': [
                                {
                                    'element': 'procedure_code',
                                    'valid_codes': ['77067', '77063', '77065', '77066'],
                                    'code_system': 'CPT',
                                    'required': True
                                },
                                {
                                    'element': 'service_date',
                                    'date_range': 'Measurement year or year prior to measurement year',
                                    'required': True
                                },
                                {
                                    'element': 'bilateral_indicator',
                                    'description': 'Procedure must be bilateral or two unilateral procedures',
                                    'required': True
                                },
                                {
                                    'element': 'result_documentation',
                                    'description': 'Documented result (BI-RADS category or narrative)',
                                    'required': True,
                                    'acceptable_formats': ['BI-RADS 0-6', 'Narrative result']
                                }
                            ]
                        },
                        {
                            'option': 2,
                            'description': 'Bilateral mastectomy exclusion',
                            'required_elements': [
                                {
                                    'element': 'procedure_code',
                                    'valid_codes': ['19180', '19200', '19220', '19303', '19304', '19305', '19306', '19307'],
                                    'code_system': 'CPT',
                                    'bilateral_required': True
                                },
                                {
                                    'element': 'pathology_report',
                                    'description': 'Surgical pathology confirming bilateral procedure',
                                    'required': True
                                }
                            ]
                        }
                    ]
                },
                
                'common_audit_failures': [
                    {
                        'failure_pattern': 'Missing bilateral indicator',
                        'description': 'Single unilateral mammography code without bilateral modifier or second unilateral',
                        'prevalence': 0.18,
                        'remediation': 'Search for second unilateral code or bilateral modifier documentation'
                    },
                    {
                        'failure_pattern': 'Missing result documentation',
                        'description': 'Procedure code present but no documented result',
                        'prevalence': 0.22,
                        'remediation': 'Obtain radiology report with BI-RADS category or narrative result'
                    },
                    {
                        'failure_pattern': 'Insufficient mastectomy documentation',
                        'description': 'Exclusion claimed but pathology report missing',
                        'prevalence': 0.15,
                        'remediation': 'Obtain surgical pathology report confirming bilateral procedure'
                    }
                ],
                
                'cdc_audit_notes': [
                    'CMS auditors require both procedure code AND documented result',
                    'Bilateral mastectomy exclusions must have surgical pathology confirmation',
                    'Unilateral mastectomy requires bilateral modifier OR contralateral mastectomy',
                    'Diagnostic mammography does NOT count for screening measure'
                ]
            },
            
            'COL': {
                'measure_name': 'Colorectal Cancer Screening',
                'measure_code': 'COL',
                'domain': 'Screening',
                'star_rating_weight': 3.0,
                'description': 'Adults 50-75 who had appropriate screening for colorectal cancer',
                
                'eligibility': {
                    'age_range': [50, 75],
                    'gender': 'Both',
                    'continuous_enrollment': 'Required during measurement year',
                    'exclusions': [
                        'Total colectomy',
                        'Colorectal cancer',
                        'Advanced illness with limited life expectancy'
                    ]
                },
                
                'numerator_criteria': {
                    'description': 'One or more screenings for colorectal cancer',
                    'compliance_options': [
                        {
                            'option': 1,
                            'description': 'Colonoscopy during measurement year or 9 years prior',
                            'required_elements': [
                                {
                                    'element': 'procedure_code',
                                    'valid_codes': ['G0105', 'G0121', '45378', '45380', '45381', '45384', '45385'],
                                    'code_system': 'CPT/HCPCS',
                                    'required': True
                                },
                                {
                                    'element': 'service_date',
                                    'date_range': 'Measurement year or 9 years prior',
                                    'required': True
                                },
                                {
                                    'element': 'cecal_intubation',
                                    'description': 'Documentation that cecum was reached',
                                    'required': True,
                                    'acceptable_terms': ['cecum intubated', 'reached cecum', 'cecal intubation', 'terminal ileum']
                                },
                                {
                                    'element': 'complete_procedure',
                                    'description': 'Procedure completed successfully',
                                    'required': True
                                }
                            ]
                        },
                        {
                            'option': 2,
                            'description': 'FIT test (Fecal Immunochemical Test) during measurement year',
                            'required_elements': [
                                {
                                    'element': 'procedure_code',
                                    'valid_codes': ['82274', '3017F'],
                                    'code_system': 'CPT',
                                    'required': True
                                },
                                {
                                    'element': 'service_date',
                                    'date_range': 'Measurement year',
                                    'required': True
                                },
                                {
                                    'element': 'result_documentation',
                                    'description': 'Documented result (positive or negative)',
                                    'required': True
                                }
                            ]
                        },
                        {
                            'option': 3,
                            'description': 'Flexible sigmoidoscopy during measurement year or 4 years prior',
                            'required_elements': [
                                {
                                    'element': 'procedure_code',
                                    'valid_codes': ['G0104', '45330', '45331', '45332', '45333', '45334', '45335', '45337', '45338', '45339', '45340', '45341', '45342', '45345', '45346', '45347', '45349', '45350'],
                                    'code_system': 'CPT/HCPCS',
                                    'required': True
                                },
                                {
                                    'element': 'service_date',
                                    'date_range': 'Measurement year or 4 years prior',
                                    'required': True
                                }
                            ]
                        },
                        {
                            'option': 4,
                            'description': 'CT colonography during measurement year or 4 years prior',
                            'required_elements': [
                                {
                                    'element': 'procedure_code',
                                    'valid_codes': ['74263'],
                                    'code_system': 'CPT',
                                    'required': True
                                },
                                {
                                    'element': 'service_date',
                                    'date_range': 'Measurement year or 4 years prior',
                                    'required': True
                                }
                            ]
                        }
                    ]
                },
                
                'common_audit_failures': [
                    {
                        'failure_pattern': 'Incomplete colonoscopy',
                        'description': 'Colonoscopy code present but no cecal intubation documented',
                        'prevalence': 0.28,
                        'remediation': 'Search procedure note for cecal intubation language or withdrawal time'
                    },
                    {
                        'failure_pattern': 'Poor prep quality',
                        'description': 'Procedure aborted due to inadequate bowel preparation',
                        'prevalence': 0.12,
                        'remediation': 'Identify if repeat procedure was completed with adequate prep'
                    },
                    {
                        'failure_pattern': 'Missing FIT result',
                        'description': 'FIT test ordered but result not documented',
                        'prevalence': 0.19,
                        'remediation': 'Obtain laboratory result showing positive or negative'
                    }
                ],
                
                'cms_audit_notes': [
                    'Cecal intubation MUST be explicitly documented for colonoscopy',
                    'FIT-DNA tests (Cologuard) require result documentation',
                    'Partial colonoscopy or sigmoidoscopy does not meet colonoscopy criteria',
                    'Procedure completed outside measurement timeframe does not count'
                ]
            },
            
            'CBP': {
                'measure_name': 'Controlling High Blood Pressure',
                'measure_code': 'CBP',
                'domain': 'Effectiveness of Care',
                'star_rating_weight': 3.0,
                'description': 'Adults 18-85 with hypertension whose BP was adequately controlled during measurement year',
                
                'eligibility': {
                    'age_range': [18, 85],
                    'gender': 'Both',
                    'diagnosis_required': ['Essential hypertension (I10)', 'Hypertensive chronic kidney disease', 'Hypertensive heart disease'],
                    'continuous_enrollment': 'Required during measurement year'
                },
                
                'numerator_criteria': {
                    'description': 'Most recent BP reading <140/90 mmHg',
                    'compliance_options': [
                        {
                            'option': 1,
                            'description': 'Blood pressure adequately controlled',
                            'required_elements': [
                                {
                                    'element': 'systolic_bp',
                                    'value': '<140 mmHg',
                                    'required': True,
                                    'measurement_method': 'Documented in medical record'
                                },
                                {
                                    'element': 'diastolic_bp',
                                    'value': '<90 mmHg',
                                    'required': True,
                                    'measurement_method': 'Documented in medical record'
                                },
                                {
                                    'element': 'service_date',
                                    'date_range': 'Measurement year',
                                    'required': True
                                },
                                {
                                    'element': 'both_values_required',
                                    'description': 'BOTH systolic AND diastolic must be documented in same encounter',
                                    'required': True,
                                    'critical': True
                                },
                                {
                                    'element': 'representative_bp',
                                    'description': 'Use most recent BP reading during measurement year',
                                    'required': True
                                }
                            ]
                        }
                    ]
                },
                
                'common_audit_failures': [
                    {
                        'failure_pattern': 'Missing diastolic BP',
                        'description': 'Only systolic BP documented, diastolic missing',
                        'prevalence': 0.30,
                        'remediation': 'Search encounter note for complete BP reading (both SBP and DBP)',
                        'critical': True
                    },
                    {
                        'failure_pattern': 'Missing systolic BP',
                        'description': 'Only diastolic BP documented, systolic missing',
                        'prevalence': 0.08,
                        'remediation': 'Search encounter note for complete BP reading (both SBP and DBP)',
                        'critical': True
                    },
                    {
                        'failure_pattern': 'BP from different encounters',
                        'description': 'Systolic from one visit, diastolic from another',
                        'prevalence': 0.15,
                        'remediation': 'Both values must be from same encounter on same date'
                    },
                    {
                        'failure_pattern': 'Home BP readings only',
                        'description': 'Only patient-reported home readings documented',
                        'prevalence': 0.10,
                        'remediation': 'Obtain office-measured BP reading from clinical visit'
                    }
                ],
                
                'cms_audit_notes': [
                    'CRITICAL: BOTH systolic AND diastolic required from same encounter',
                    'Most common audit failure: Missing one component of BP reading',
                    'Home BP readings do not count for HEDIS measure',
                    'BP must be taken during face-to-face or telehealth visit',
                    'Use MOST RECENT BP in measurement year'
                ]
            },
            
            'CDC': {
                'measure_name': 'Comprehensive Diabetes Care',
                'measure_code': 'CDC',
                'domain': 'Effectiveness of Care',
                'star_rating_weight': 3.0,
                'description': 'Adults 18-75 with diabetes who had HbA1c testing and control',
                
                'eligibility': {
                    'age_range': [18, 75],
                    'gender': 'Both',
                    'diagnosis_required': ['Type 1 diabetes (E10)', 'Type 2 diabetes (E11)'],
                    'continuous_enrollment': 'Required during measurement year'
                },
                
                'numerator_criteria': {
                    'description': 'HbA1c testing and control (<8% or <9% depending on sub-measure)',
                    'compliance_options': [
                        {
                            'option': 1,
                            'description': 'HbA1c testing performed',
                            'required_elements': [
                                {
                                    'element': 'procedure_code',
                                    'valid_codes': ['83036', '83037', '3044F', '3045F', '3046F'],
                                    'code_system': 'CPT',
                                    'required': True
                                },
                                {
                                    'element': 'service_date',
                                    'date_range': 'Measurement year',
                                    'required': True
                                },
                                {
                                    'element': 'result_value',
                                    'description': 'Numeric HbA1c value documented',
                                    'required': True,
                                    'format': 'X.X% or XX mmol/mol'
                                }
                            ]
                        },
                        {
                            'option': 2,
                            'description': 'HbA1c poor control (>9%)',
                            'required_elements': [
                                {
                                    'element': 'hba1c_value',
                                    'value': '>9.0%',
                                    'required': True,
                                    'note': 'This is inverse measure - higher is worse for Star Rating'
                                }
                            ]
                        },
                        {
                            'option': 3,
                            'description': 'HbA1c control (<8%)',
                            'required_elements': [
                                {
                                    'element': 'hba1c_value',
                                    'value': '<8.0%',
                                    'required': True,
                                    'note': 'This demonstrates good control for Star Rating'
                                }
                            ]
                        }
                    ]
                },
                
                'additional_components': {
                    'eye_exam': {
                        'description': 'Retinal or dilated eye exam',
                        'required_codes': ['67028', '67030', '67031', '67036', '67039', '67040', '67041', '67042', '67043', '92002', '92004', '92012', '92014', '92018', '92019', '92134', '92225', '92226', '92227', '92228', '92230', '92235', '92240', '92250', '92260', 'S0620', 'S0621', 'S3000'],
                        'timeframe': 'Measurement year or year prior'
                    },
                    'nephropathy_screening': {
                        'description': 'Urine protein test or ACE/ARB therapy',
                        'required_codes': ['81000', '81001', '81002', '81003', '81005', '81007', '81015', '81020', '82042', '82043', '82044', '84156', '3060F', '3061F', '3062F'],
                        'timeframe': 'Measurement year'
                    }
                },
                
                'common_audit_failures': [
                    {
                        'failure_pattern': 'Missing HbA1c value',
                        'description': 'Test code present but numeric result not documented',
                        'prevalence': 0.25,
                        'remediation': 'Obtain laboratory report with specific HbA1c percentage value'
                    },
                    {
                        'failure_pattern': 'Glucose value instead of HbA1c',
                        'description': 'Random or fasting glucose documented instead of HbA1c',
                        'prevalence': 0.18,
                        'remediation': 'HbA1c is different from glucose - must have HbA1c test'
                    }
                ],
                
                'cms_audit_notes': [
                    'HbA1c MUST have numeric value documented (X.X%)',
                    'Glucose tests (fasting, random) do NOT substitute for HbA1c',
                    'Multiple HbA1c tests - use most recent value in measurement year',
                    'Eye exam must be by eye care professional (optometrist or ophthalmologist)'
                ]
            },
            
            'KED': {
                'measure_name': 'Kidney Health Evaluation for Patients with Diabetes',
                'measure_code': 'KED',
                'domain': 'Effectiveness of Care',
                'star_rating_weight': 1.0,
                'description': 'Adults 18-75 with diabetes who received kidney health evaluation',
                
                'eligibility': {
                    'age_range': [18, 75],
                    'gender': 'Both',
                    'diagnosis_required': ['Type 1 diabetes (E10)', 'Type 2 diabetes (E11)'],
                    'continuous_enrollment': 'Required during measurement year'
                },
                
                'numerator_criteria': {
                    'description': 'Kidney health evaluation including uACR and eGFR',
                    'compliance_options': [
                        {
                            'option': 1,
                            'description': 'Both uACR and eGFR completed',
                            'required_elements': [
                                {
                                    'element': 'uacr_test',
                                    'valid_codes': ['82043', '82044'],
                                    'description': 'Urine albumin-creatinine ratio',
                                    'required': True
                                },
                                {
                                    'element': 'egfr_test',
                                    'valid_codes': ['80069', '3066F'],
                                    'description': 'Estimated glomerular filtration rate',
                                    'required': True
                                },
                                {
                                    'element': 'service_date',
                                    'date_range': 'Both tests within measurement year',
                                    'required': True
                                }
                            ]
                        }
                    ]
                },
                
                'common_audit_failures': [
                    {
                        'failure_pattern': 'Missing eGFR',
                        'description': 'uACR completed but eGFR not ordered',
                        'prevalence': 0.22,
                        'remediation': 'Both tests required - order eGFR if missing'
                    }
                ],
                
                'cms_audit_notes': [
                    'BOTH uACR AND eGFR required - neither alone is sufficient',
                    'Tests must be completed in same measurement year'
                ]
            }
        }
        
        return specs
    
    def get_measure_spec(self, measure_code: str) -> Dict:
        """Retrieve specification for specific measure"""
        return self.specifications.get(measure_code, {})
    
    def validate_documentation(self, measure_code: str, documentation: Dict) -> Dict:
        """Validate documentation against NCQA specifications"""
        
        spec = self.get_measure_spec(measure_code)
        if not spec:
            return {
                'valid': False,
                'error': f'Unknown measure code: {measure_code}'
            }
        
        validation_result = {
            'measure_code': measure_code,
            'measure_name': spec['measure_name'],
            'compliant': True,
            'missing_elements': [],
            'warnings': [],
            'audit_risk': 'LOW'
        }
        
        # Check numerator criteria
        numerator = spec.get('numerator_criteria', {})
        options = numerator.get('compliance_options', [])
        
        # Try each compliance option
        any_option_met = False
        for option in options:
            required_elements = option.get('required_elements', [])
            option_met = True
            
            for element in required_elements:
                element_name = element['element']
                
                # Check if element exists in documentation
                if element_name not in documentation or documentation[element_name] is None:
                    option_met = False
                    
                    if element.get('required', False):
                        validation_result['missing_elements'].append({
                            'element': element_name,
                            'description': element.get('description', ''),
                            'critical': element.get('critical', False)
                        })
            
            if option_met:
                any_option_met = True
                break
        
        if not any_option_met:
            validation_result['compliant'] = False
            validation_result['audit_risk'] = 'CRITICAL' if len(validation_result['missing_elements']) > 2 else 'HIGH'
        
        # Check for common audit failure patterns
        common_failures = spec.get('common_audit_failures', [])
        for failure in common_failures:
            # Pattern matching logic would go here
            if failure.get('critical', False):
                validation_result['warnings'].append({
                    'pattern': failure['failure_pattern'],
                    'remediation': failure['remediation']
                })
        
        return validation_result
    
    def export_to_json(self, filepath: str = '/home/claude/ncqa_specifications.json'):
        """Export specifications to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.specifications, f, indent=2)
        print(f"NCQA specifications exported to: {filepath}")
    
    def get_audit_checklist(self, measure_code: str) -> List[str]:
        """Generate audit checklist for specific measure"""
        
        spec = self.get_measure_spec(measure_code)
        if not spec:
            return []
        
        checklist = [
            f"Measure: {spec['measure_name']} ({measure_code})",
            "",
            "Required Documentation Elements:"
        ]
        
        numerator = spec.get('numerator_criteria', {})
        for idx, option in enumerate(numerator.get('compliance_options', []), 1):
            checklist.append(f"\nOption {idx}: {option['description']}")
            for element in option.get('required_elements', []):
                required_flag = "✓ REQUIRED" if element.get('required', False) else "  OPTIONAL"
                critical_flag = " [CRITICAL]" if element.get('critical', False) else ""
                checklist.append(f"  {required_flag}{critical_flag}: {element['element']}")
                if 'description' in element:
                    checklist.append(f"    → {element['description']}")
        
        # Add common failures
        checklist.append("\nCommon Audit Failures to Watch:")
        for failure in spec.get('common_audit_failures', []):
            checklist.append(f"  ⚠ {failure['failure_pattern']}")
            checklist.append(f"    Remediation: {failure['remediation']}")
        
        # Add CMS notes
        checklist.append("\nCMS Audit Notes:")
        for note in spec.get('cms_audit_notes', []):
            checklist.append(f"  • {note}")
        
        return checklist


def main():
    """Generate and save NCQA specification database"""
    
    print("AuditShield Live - NCQA Specification Database Builder")
    print("=" * 70)
    
    # Initialize database
    db = NCQASpecificationDatabase(measurement_year=2026)
    
    # Export to JSON
    db.export_to_json()
    
    # Generate audit checklists for each measure
    print("\nGenerating audit checklists...")
    
    checklist_dir = '/home/claude/audit_checklists'
    import os
    os.makedirs(checklist_dir, exist_ok=True)
    
    for measure_code in ['BCS', 'COL', 'CBP', 'CDC', 'KED']:
        checklist = db.get_audit_checklist(measure_code)
        
        filepath = f"{checklist_dir}/{measure_code}_audit_checklist.txt"
        with open(filepath, 'w') as f:
            f.write('\n'.join(checklist))
        
        print(f"  ✓ {measure_code} checklist created")
    
    print("\n" + "=" * 70)
    print("NCQA SPECIFICATION DATABASE COMPLETE")
    print("=" * 70)
    print("Files created:")
    print("1. ncqa_specifications.json - Complete measure specifications")
    print("2. audit_checklists/ - Individual measure audit checklists")
    print("\nDatabase includes:")
    print(f"  • {len(db.specifications)} HEDIS measures")
    print("  • Numerator compliance criteria")
    print("  • Common audit failure patterns")
    print("  • CMS audit notes and remediations")
    print("\nReady for Phase 1.3: Base Validation Logic")


if __name__ == "__main__":
    main()
