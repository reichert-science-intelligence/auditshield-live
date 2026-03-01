"""
AuditShield Live - Layer 1: Document Intelligence Engine
NLP extraction of clinical entities from medical documentation

Author: Robert Hucks (Healthcare Data Scientist)
Purpose: Extract structured data from unstructured clinical notes
Processing Target: <1.2 seconds per chart
"""

import pandas as pd
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import json

class DocumentIntelligenceEngine:
    """
    Layer 1: Extract clinical entities from unstructured documentation
    Uses pattern matching and NLP to identify procedure codes, diagnoses, 
    measurements, and other HEDIS-relevant data points
    """
    
    def __init__(self):
        # Clinical entity patterns
        self.patterns = self._initialize_patterns()
        
        # Performance tracking
        self.processing_times = []
        
    def _initialize_patterns(self) -> Dict:
        """Initialize regex patterns for clinical entity extraction"""
        
        return {
            # Procedure codes
            'cpt_codes': re.compile(r'\b(G?\d{4,5}[A-Z]?)\b'),
            'icd10_codes': re.compile(r'\b([A-Z]\d{2}(?:\.\d{1,3})?)\b'),
            
            # Blood pressure patterns
            'bp_reading': re.compile(r'\b(\d{2,3})\s*/\s*(\d{2,3})\s*(?:mmHg|mm Hg)?\b', re.IGNORECASE),
            'systolic_only': re.compile(r'\bSBP\s*:?\s*(\d{2,3})\b', re.IGNORECASE),
            'diastolic_only': re.compile(r'\bDBP\s*:?\s*(\d{2,3})\b', re.IGNORECASE),
            
            # HbA1c patterns
            'hba1c_value': re.compile(r'\bHbA1c\s*:?\s*(\d+\.?\d*)\s*%', re.IGNORECASE),
            'a1c_value': re.compile(r'\bA1c\s*:?\s*(\d+\.?\d*)\s*%?', re.IGNORECASE),
            
            # Mammography results
            'birads': re.compile(r'\bBI-?RADS\s*(?:Category\s*)?(\d)\b', re.IGNORECASE),
            'bilateral': re.compile(r'\b(bilateral|both breasts)\b', re.IGNORECASE),
            
            # Colonoscopy completion
            'cecal_intubation': re.compile(r'\b(cecum\s+(?:intubated|reached|visualized)|cecal\s+intubation|terminal\s+ileum)\b', re.IGNORECASE),
            'withdrawal_time': re.compile(r'\bwithdrawal\s+time\s*:?\s*(\d+)\s*(?:min|minutes)', re.IGNORECASE),
            
            # Dates
            'service_date': re.compile(r'\b(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})\b'),
            
            # Provider information
            'provider_name': re.compile(r'\bDr\.\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),?\s*MD\b'),
            
            # Facility
            'facility_name': re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Center|Hospital|Clinic|Associates|Imaging))\b'),
            
            # Lab values
            'egfr_value': re.compile(r'\beGFR\s*:?\s*(\d+)\s*(?:mL/min)?', re.IGNORECASE),
            'creatinine': re.compile(r'\b(?:serum\s+)?creatinine\s*:?\s*(\d+\.?\d*)\s*(?:mg/dL)?', re.IGNORECASE),
        }
    
    def extract_from_chart(self, chart_row: pd.Series) -> Dict:
        """
        Extract all clinical entities from a chart
        
        Args:
            chart_row: Pandas Series with chart data including clinical_note
            
        Returns:
            Dictionary of extracted entities with confidence scores
        """
        start_time = datetime.now()
        
        clinical_note = str(chart_row.get('clinical_note', ''))
        
        extracted = {
            'chart_id': chart_row.get('chart_id'),
            'extraction_timestamp': start_time.isoformat(),
            'entities': {},
            'confidence_scores': {},
            'extraction_methods': {}
        }
        
        # Extract based on measure type
        measure_code = chart_row.get('measure_code')
        
        if measure_code == 'BCS':
            extracted = self._extract_bcs_entities(chart_row, clinical_note, extracted)
        elif measure_code == 'COL':
            extracted = self._extract_col_entities(chart_row, clinical_note, extracted)
        elif measure_code == 'CBP':
            extracted = self._extract_cbp_entities(chart_row, clinical_note, extracted)
        elif measure_code == 'CDC':
            extracted = self._extract_cdc_entities(chart_row, clinical_note, extracted)
        elif measure_code == 'KED':
            extracted = self._extract_ked_entities(chart_row, clinical_note, extracted)
        
        # Extract common entities for all measures
        extracted = self._extract_common_entities(chart_row, clinical_note, extracted)
        
        # Calculate processing time
        end_time = datetime.now()
        extracted['processing_time_ms'] = (end_time - start_time).total_seconds() * 1000
        self.processing_times.append(extracted['processing_time_ms'])
        
        return extracted
    
    def _extract_bcs_entities(self, chart: pd.Series, note: str, extracted: Dict) -> Dict:
        """Extract Breast Cancer Screening specific entities"""
        
        # Look for BI-RADS category
        birads_match = self.patterns['birads'].search(note)
        if birads_match:
            extracted['entities']['birads_category'] = int(birads_match.group(1))
            extracted['confidence_scores']['birads_category'] = 0.95
            extracted['extraction_methods']['birads_category'] = 'regex_pattern'
        
        # Check for bilateral indicator
        bilateral_match = self.patterns['bilateral'].search(note)
        if bilateral_match:
            extracted['entities']['bilateral_documented'] = True
            extracted['confidence_scores']['bilateral_documented'] = 0.90
            extracted['extraction_methods']['bilateral_documented'] = 'regex_pattern'
        
        # Check for procedure code in note or existing field
        if pd.notna(chart.get('procedure_code')):
            extracted['entities']['procedure_code'] = chart['procedure_code']
            extracted['confidence_scores']['procedure_code'] = 1.0
            extracted['extraction_methods']['procedure_code'] = 'structured_field'
        else:
            # Try to extract from note
            code_match = self.patterns['cpt_codes'].search(note)
            if code_match:
                extracted['entities']['procedure_code'] = code_match.group(1)
                extracted['confidence_scores']['procedure_code'] = 0.75
                extracted['extraction_methods']['procedure_code'] = 'note_extraction'
        
        # Check for result
        if pd.notna(chart.get('result')):
            extracted['entities']['result_documented'] = True
            extracted['entities']['result_text'] = str(chart['result'])
            extracted['confidence_scores']['result_documented'] = 1.0
            extracted['extraction_methods']['result_documented'] = 'structured_field'
        elif 'negative' in note.lower() or 'bi-rads' in note.lower():
            extracted['entities']['result_documented'] = True
            extracted['entities']['result_text'] = 'Result mentioned in note'
            extracted['confidence_scores']['result_documented'] = 0.70
            extracted['extraction_methods']['result_documented'] = 'note_inference'
        
        return extracted
    
    def _extract_col_entities(self, chart: pd.Series, note: str, extracted: Dict) -> Dict:
        """Extract Colorectal Cancer Screening specific entities"""
        
        # Check for cecal intubation
        cecal_match = self.patterns['cecal_intubation'].search(note)
        if cecal_match:
            extracted['entities']['cecal_intubation_documented'] = True
            extracted['entities']['cecal_intubation_text'] = cecal_match.group(1)
            extracted['confidence_scores']['cecal_intubation_documented'] = 0.95
            extracted['extraction_methods']['cecal_intubation_documented'] = 'regex_pattern'
        else:
            extracted['entities']['cecal_intubation_documented'] = False
            extracted['confidence_scores']['cecal_intubation_documented'] = 0.85
            extracted['extraction_methods']['cecal_intubation_documented'] = 'absence_detection'
        
        # Check for withdrawal time (indicator of complete procedure)
        withdrawal_match = self.patterns['withdrawal_time'].search(note)
        if withdrawal_match:
            extracted['entities']['withdrawal_time_minutes'] = int(withdrawal_match.group(1))
            extracted['confidence_scores']['withdrawal_time_minutes'] = 0.90
            extracted['extraction_methods']['withdrawal_time_minutes'] = 'regex_pattern'
            
            # Withdrawal time ≥6 minutes suggests complete procedure
            if extracted['entities']['withdrawal_time_minutes'] >= 6:
                extracted['entities']['procedure_quality_adequate'] = True
        
        # Procedure code
        if pd.notna(chart.get('procedure_code')):
            extracted['entities']['procedure_code'] = chart['procedure_code']
            extracted['confidence_scores']['procedure_code'] = 1.0
            extracted['extraction_methods']['procedure_code'] = 'structured_field'
        
        return extracted
    
    def _extract_cbp_entities(self, chart: pd.Series, note: str, extracted: Dict) -> Dict:
        """Extract Controlling Blood Pressure specific entities"""
        
        # Priority 1: Check structured fields
        if pd.notna(chart.get('systolic_bp')) and pd.notna(chart.get('diastolic_bp')):
            extracted['entities']['systolic_bp'] = chart['systolic_bp']
            extracted['entities']['diastolic_bp'] = chart['diastolic_bp']
            extracted['entities']['bp_both_documented'] = True
            extracted['confidence_scores']['systolic_bp'] = 1.0
            extracted['confidence_scores']['diastolic_bp'] = 1.0
            extracted['extraction_methods']['systolic_bp'] = 'structured_field'
            extracted['extraction_methods']['diastolic_bp'] = 'structured_field'
        
        # Priority 2: Look for standard BP reading format (128/76)
        elif not extracted['entities'].get('bp_both_documented', False):
            bp_match = self.patterns['bp_reading'].search(note)
            if bp_match:
                extracted['entities']['systolic_bp'] = int(bp_match.group(1))
                extracted['entities']['diastolic_bp'] = int(bp_match.group(2))
                extracted['entities']['bp_both_documented'] = True
                extracted['confidence_scores']['systolic_bp'] = 0.95
                extracted['confidence_scores']['diastolic_bp'] = 0.95
                extracted['extraction_methods']['systolic_bp'] = 'note_extraction'
                extracted['extraction_methods']['diastolic_bp'] = 'note_extraction'
        
        # Priority 3: Look for individual SBP/DBP notations
        if not extracted['entities'].get('systolic_bp'):
            sbp_match = self.patterns['systolic_only'].search(note)
            if sbp_match:
                extracted['entities']['systolic_bp'] = int(sbp_match.group(1))
                extracted['confidence_scores']['systolic_bp'] = 0.85
                extracted['extraction_methods']['systolic_bp'] = 'note_extraction'
        
        if not extracted['entities'].get('diastolic_bp'):
            dbp_match = self.patterns['diastolic_only'].search(note)
            if dbp_match:
                extracted['entities']['diastolic_bp'] = int(dbp_match.group(1))
                extracted['confidence_scores']['diastolic_bp'] = 0.85
                extracted['extraction_methods']['diastolic_bp'] = 'note_extraction'
        
        # Critical flag: Both values present?
        if 'systolic_bp' in extracted['entities'] and 'diastolic_bp' in extracted['entities']:
            extracted['entities']['bp_both_documented'] = True
            
            # Check if from same encounter (both from note or both from structured fields)
            sbp_method = extracted['extraction_methods'].get('systolic_bp')
            dbp_method = extracted['extraction_methods'].get('diastolic_bp')
            
            if sbp_method == dbp_method:
                extracted['entities']['bp_same_encounter'] = True
                extracted['confidence_scores']['bp_same_encounter'] = 0.95
            else:
                extracted['entities']['bp_same_encounter'] = False
                extracted['confidence_scores']['bp_same_encounter'] = 0.60
                extracted['warnings'] = extracted.get('warnings', [])
                extracted['warnings'].append('SBP and DBP from different sources - may not be same encounter')
        else:
            extracted['entities']['bp_both_documented'] = False
        
        return extracted
    
    def _extract_cdc_entities(self, chart: pd.Series, note: str, extracted: Dict) -> Dict:
        """Extract Comprehensive Diabetes Care specific entities"""
        
        # HbA1c value - Priority 1: Structured field
        if pd.notna(chart.get('hba1c_value')):
            extracted['entities']['hba1c_value'] = chart['hba1c_value']
            extracted['confidence_scores']['hba1c_value'] = 1.0
            extracted['extraction_methods']['hba1c_value'] = 'structured_field'
        else:
            # Priority 2: Extract from note
            hba1c_match = self.patterns['hba1c_value'].search(note)
            if hba1c_match:
                extracted['entities']['hba1c_value'] = float(hba1c_match.group(1))
                extracted['confidence_scores']['hba1c_value'] = 0.90
                extracted['extraction_methods']['hba1c_value'] = 'note_extraction'
            else:
                # Try A1c variant
                a1c_match = self.patterns['a1c_value'].search(note)
                if a1c_match:
                    extracted['entities']['hba1c_value'] = float(a1c_match.group(1))
                    extracted['confidence_scores']['hba1c_value'] = 0.85
                    extracted['extraction_methods']['hba1c_value'] = 'note_extraction'
        
        # Check if HbA1c is controlled (<8%)
        if 'hba1c_value' in extracted['entities']:
            value = extracted['entities']['hba1c_value']
            extracted['entities']['hba1c_controlled'] = value < 8.0
            extracted['entities']['hba1c_poor_control'] = value >= 9.0
        
        # Eye exam
        if chart.get('eye_exam_completed', False):
            extracted['entities']['eye_exam_documented'] = True
            extracted['confidence_scores']['eye_exam_documented'] = 1.0
            extracted['extraction_methods']['eye_exam_documented'] = 'structured_field'
        elif 'retinal' in note.lower() or 'eye exam' in note.lower() or 'ophthalmol' in note.lower():
            extracted['entities']['eye_exam_documented'] = True
            extracted['confidence_scores']['eye_exam_documented'] = 0.70
            extracted['extraction_methods']['eye_exam_documented'] = 'note_inference'
        
        # Nephropathy screening
        if chart.get('nephropathy_screening', False):
            extracted['entities']['nephropathy_screening_documented'] = True
            extracted['confidence_scores']['nephropathy_screening_documented'] = 1.0
            extracted['extraction_methods']['nephropathy_screening_documented'] = 'structured_field'
        elif 'microalbumin' in note.lower() or 'uacr' in note.lower() or 'ace inhibitor' in note.lower():
            extracted['entities']['nephropathy_screening_documented'] = True
            extracted['confidence_scores']['nephropathy_screening_documented'] = 0.70
            extracted['extraction_methods']['nephropathy_screening_documented'] = 'note_inference'
        
        return extracted
    
    def _extract_ked_entities(self, chart: pd.Series, note: str, extracted: Dict) -> Dict:
        """Extract Kidney Health Evaluation specific entities"""
        
        # eGFR value
        egfr_match = self.patterns['egfr_value'].search(note)
        if egfr_match:
            extracted['entities']['egfr_value'] = int(egfr_match.group(1))
            extracted['confidence_scores']['egfr_value'] = 0.90
            extracted['extraction_methods']['egfr_value'] = 'note_extraction'
        
        # uACR mentioned?
        if 'uacr' in note.lower() or 'albumin' in note.lower() and 'creatinine' in note.lower():
            extracted['entities']['uacr_documented'] = True
            extracted['confidence_scores']['uacr_documented'] = 0.75
            extracted['extraction_methods']['uacr_documented'] = 'note_inference'
        
        return extracted
    
    def _extract_common_entities(self, chart: pd.Series, note: str, extracted: Dict) -> Dict:
        """Extract entities common to all measures"""
        
        # Service date
        if pd.notna(chart.get('service_date')):
            extracted['entities']['service_date'] = str(chart['service_date'])
            extracted['confidence_scores']['service_date'] = 1.0
            extracted['extraction_methods']['service_date'] = 'structured_field'
        else:
            date_match = self.patterns['service_date'].search(note)
            if date_match:
                extracted['entities']['service_date'] = date_match.group(1)
                extracted['confidence_scores']['service_date'] = 0.80
                extracted['extraction_methods']['service_date'] = 'note_extraction'
        
        # Provider name
        if pd.notna(chart.get('ordering_provider')):
            extracted['entities']['provider_name'] = chart['ordering_provider']
            extracted['confidence_scores']['provider_name'] = 1.0
            extracted['extraction_methods']['provider_name'] = 'structured_field'
        else:
            provider_match = self.patterns['provider_name'].search(note)
            if provider_match:
                extracted['entities']['provider_name'] = f"Dr. {provider_match.group(1)}, MD"
                extracted['confidence_scores']['provider_name'] = 0.85
                extracted['extraction_methods']['provider_name'] = 'note_extraction'
        
        # Facility name
        if pd.notna(chart.get('performing_facility')):
            extracted['entities']['facility_name'] = chart['performing_facility']
            extracted['confidence_scores']['facility_name'] = 1.0
            extracted['extraction_methods']['facility_name'] = 'structured_field'
        else:
            facility_match = self.patterns['facility_name'].search(note)
            if facility_match:
                extracted['entities']['facility_name'] = facility_match.group(1)
                extracted['confidence_scores']['facility_name'] = 0.75
                extracted['extraction_methods']['facility_name'] = 'note_extraction'
        
        return extracted
    
    def get_performance_stats(self) -> Dict:
        """Calculate processing performance statistics"""
        
        if not self.processing_times:
            return {'error': 'No processing times recorded'}
        
        import statistics
        
        return {
            'total_charts_processed': len(self.processing_times),
            'average_time_ms': statistics.mean(self.processing_times),
            'median_time_ms': statistics.median(self.processing_times),
            'min_time_ms': min(self.processing_times),
            'max_time_ms': max(self.processing_times),
            'target_time_ms': 1200,  # 1.2 seconds
            'meets_target': statistics.mean(self.processing_times) < 1200
        }


def main():
    """Test document intelligence engine on synthetic charts"""
    
    print("\n" + "=" * 70)
    print("AUDITSHIELD LIVE - LAYER 1: DOCUMENT INTELLIGENCE")
    print("Phase 2.1: NLP Entity Extraction")
    print("=" * 70 + "\n")
    
    # Load chart data
    charts_df = pd.read_csv('/home/claude/chart_documentation.csv')
    
    print(f"Processing {len(charts_df)} charts through Layer 1...")
    
    # Initialize engine
    engine = DocumentIntelligenceEngine()
    
    # Process all charts
    extraction_results = []
    for idx, chart in charts_df.iterrows():
        result = engine.extract_from_chart(chart)
        extraction_results.append(result)
        
        if (idx + 1) % 100 == 0:
            print(f"  Processed {idx + 1}/{len(charts_df)} charts...")
    
    print(f"  Processed {len(charts_df)}/{len(charts_df)} charts ✓")
    
    # Convert to DataFrame
    results_df = pd.DataFrame(extraction_results)
    
    # Performance statistics
    perf_stats = engine.get_performance_stats()
    
    print("\n" + "=" * 70)
    print("LAYER 1 PROCESSING PERFORMANCE")
    print("=" * 70)
    print(f"Total Charts: {perf_stats['total_charts_processed']}")
    print(f"Average Processing Time: {perf_stats['average_time_ms']:.2f} ms")
    print(f"Median Processing Time: {perf_stats['median_time_ms']:.2f} ms")
    print(f"Min/Max Time: {perf_stats['min_time_ms']:.2f} / {perf_stats['max_time_ms']:.2f} ms")
    print(f"Target Time: {perf_stats['target_time_ms']} ms (1.2 seconds)")
    print(f"Meets Target: {'✓ YES' if perf_stats['meets_target'] else '✗ NO'}")
    
    # Entity extraction statistics
    print("\n" + "=" * 70)
    print("ENTITY EXTRACTION SUMMARY")
    print("=" * 70)
    
    # Count entities extracted
    total_entities = sum(len(result['entities']) for result in extraction_results)
    avg_entities_per_chart = total_entities / len(extraction_results)
    
    print(f"Total Entities Extracted: {total_entities}")
    print(f"Average Entities per Chart: {avg_entities_per_chart:.1f}")
    
    # Confidence score distribution
    all_confidence_scores = []
    for result in extraction_results:
        all_confidence_scores.extend(result['confidence_scores'].values())
    
    if all_confidence_scores:
        import statistics
        print(f"\nConfidence Score Statistics:")
        print(f"  Average Confidence: {statistics.mean(all_confidence_scores):.3f}")
        print(f"  Median Confidence: {statistics.median(all_confidence_scores):.3f}")
        print(f"  Min/Max Confidence: {min(all_confidence_scores):.3f} / {max(all_confidence_scores):.3f}")
    
    # Extraction method breakdown
    extraction_methods_count = {}
    for result in extraction_results:
        for method in result['extraction_methods'].values():
            extraction_methods_count[method] = extraction_methods_count.get(method, 0) + 1
    
    print(f"\nExtraction Methods Used:")
    for method, count in sorted(extraction_methods_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {method}: {count} entities ({count/total_entities*100:.1f}%)")
    
    # Save results
    print("\n" + "=" * 70)
    print("Saving Layer 1 extraction results...")
    
    # Save detailed results to JSON
    with open('/home/claude/layer1_extraction_results.json', 'w') as f:
        json.dump(extraction_results, f, indent=2)
    print("  ✓ layer1_extraction_results.json")
    
    # Save performance stats
    with open('/home/claude/layer1_performance.json', 'w') as f:
        json.dump(perf_stats, f, indent=2)
    print("  ✓ layer1_performance.json")
    
    print("\n" + "=" * 70)
    print("LAYER 1 DOCUMENT INTELLIGENCE - COMPLETE")
    print("=" * 70)
    print("\nNext: Layer 3 - Self-Correction Validation")
    print("  • Cross-source verification")
    print("  • False positive detection")
    print("  • False negative detection")
    print("  • Confidence score refinement")


if __name__ == "__main__":
    main()
