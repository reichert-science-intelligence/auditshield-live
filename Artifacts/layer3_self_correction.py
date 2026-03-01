"""
AuditShield Live - Layer 3: Self-Correction Validation Engine
Cross-source verification and error detection

Author: Robert Hucks (Healthcare Data Scientist)
Purpose: Validate Layer 1 extractions and Layer 2 specifications against multiple sources
Processing Target: <0.8 seconds per chart
Accuracy Target: Reduce false positives/negatives by 95%
"""

import pandas as pd
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class SelfCorrectionEngine:
    """
    Layer 3: Cross-validate findings and detect false positives/negatives
    
    Validates extraction and specification results by:
    - Checking consistency across multiple data sources
    - Detecting overclaims (false positives)
    - Detecting missed documentation (false negatives)
    - Refining confidence scores based on agreement
    """
    
    def __init__(self):
        self.processing_times = []
        self.corrections_made = []
        
    def validate_extraction(self, 
                          layer1_result: Dict, 
                          chart_row: pd.Series,
                          validation_result: Dict) -> Dict:
        """
        Cross-validate Layer 1 extraction against original chart and Layer 2 validation
        
        Args:
            layer1_result: Output from Layer 1 document intelligence
            chart_row: Original chart data
            validation_result: Output from Layer 2 specification matching
            
        Returns:
            Corrected validation with adjusted confidence scores and flags
        """
        start_time = datetime.now()
        
        corrected = {
            'chart_id': chart_row.get('chart_id'),
            'measure_code': chart_row.get('measure_code'),
            'correction_timestamp': start_time.isoformat(),
            'original_compliant': validation_result.get('compliant', False),
            'original_risk_level': validation_result.get('risk_level', 'UNKNOWN'),
            'corrections_applied': [],
            'false_positives_detected': [],
            'false_negatives_detected': [],
            'confidence_adjustments': {},
            'final_compliant': validation_result.get('compliant', False),
            'final_risk_level': validation_result.get('risk_level', 'UNKNOWN'),
            'final_compliance_score': validation_result.get('compliance_score', 0)
        }
        
        # Apply measure-specific corrections
        measure_code = chart_row.get('measure_code')
        
        if measure_code == 'BCS':
            corrected = self._correct_bcs(layer1_result, chart_row, validation_result, corrected)
        elif measure_code == 'COL':
            corrected = self._correct_col(layer1_result, chart_row, validation_result, corrected)
        elif measure_code == 'CBP':
            corrected = self._correct_cbp(layer1_result, chart_row, validation_result, corrected)
        elif measure_code == 'CDC':
            corrected = self._correct_cdc(layer1_result, chart_row, validation_result, corrected)
        elif measure_code == 'KED':
            corrected = self._correct_ked(layer1_result, chart_row, validation_result, corrected)
        
        # Recalculate final compliance based on corrections
        corrected = self._recalculate_compliance(corrected, validation_result)
        
        # Calculate processing time
        end_time = datetime.now()
        corrected['processing_time_ms'] = (end_time - start_time).total_seconds() * 1000
        self.processing_times.append(corrected['processing_time_ms'])
        
        # Track if corrections changed the outcome
        if corrected['final_compliant'] != corrected['original_compliant']:
            self.corrections_made.append({
                'chart_id': corrected['chart_id'],
                'measure_code': measure_code,
                'original_status': 'compliant' if corrected['original_compliant'] else 'non-compliant',
                'final_status': 'compliant' if corrected['final_compliant'] else 'non-compliant',
                'corrections': corrected['corrections_applied']
            })
        
        return corrected
    
    def _correct_bcs(self, layer1: Dict, chart: pd.Series, layer2: Dict, corrected: Dict) -> Dict:
        """Self-correction for Breast Cancer Screening"""
        
        entities = layer1.get('entities', {})
        confidence = layer1.get('confidence_scores', {})
        
        # Check 1: Procedure code present but no result
        if entities.get('procedure_code') and not entities.get('result_documented'):
            # FALSE POSITIVE: Having code alone doesn't mean screening completed
            corrected['false_positives_detected'].append({
                'element': 'screening_completion',
                'issue': 'Procedure code present but no result documented',
                'risk': 'CMS auditors require documented result, not just billing code'
            })
            
            # Increase severity if this was marked as compliant
            if layer2.get('compliant', False):
                corrected['corrections_applied'].append({
                    'correction': 'Downgraded from compliant to non-compliant',
                    'reason': 'Missing result documentation despite procedure code',
                    'severity': 'CRITICAL'
                })
                corrected['final_compliant'] = False
                corrected['final_risk_level'] = 'HIGH'
        
        # Check 2: Result "documented" but only inferred from note
        result_method = layer1.get('extraction_methods', {}).get('result_documented')
        if result_method == 'note_inference' and confidence.get('result_documented', 1.0) < 0.8:
            # FALSE POSITIVE: Weak inference may not pass CMS audit
            corrected['false_positives_detected'].append({
                'element': 'result_documentation',
                'issue': 'Result inferred from note language, not explicitly documented',
                'risk': 'Low confidence extraction may fail CMS validation'
            })
            
            corrected['confidence_adjustments']['result_documented'] = {
                'original': confidence.get('result_documented', 0),
                'adjusted': 0.50,  # Reduce confidence significantly
                'reason': 'Inference-based extraction insufficient for audit'
            }
        
        # Check 3: Bilateral documentation
        if not entities.get('bilateral_documented'):
            # Check if this is actually a bilateral procedure code
            bilateral_codes = ['77067']  # Codes that are inherently bilateral
            if chart.get('procedure_code') in bilateral_codes:
                # FALSE NEGATIVE: Code is bilateral but we didn't detect it
                corrected['false_negatives_detected'].append({
                    'element': 'bilateral_indicator',
                    'issue': 'Procedure code 77067 is inherently bilateral',
                    'correction': 'Marked bilateral as documented based on procedure code'
                })
                
                corrected['corrections_applied'].append({
                    'correction': 'Added bilateral documentation based on procedure code',
                    'reason': 'CPT 77067 is inherently bilateral mammography',
                    'severity': 'MEDIUM'
                })
                
                # Potentially upgrade compliance if this was the only issue
                if not layer2.get('compliant') and len(layer2.get('missing_elements', [])) == 1:
                    if layer2['missing_elements'][0]['element'] == 'bilateral_indicator':
                        corrected['final_compliant'] = True
                        corrected['final_risk_level'] = 'LOW'
        
        return corrected
    
    def _correct_col(self, layer1: Dict, chart: pd.Series, layer2: Dict, corrected: Dict) -> Dict:
        """Self-correction for Colorectal Cancer Screening"""
        
        entities = layer1.get('entities', {})
        
        # Check 1: Cecal intubation documented but withdrawal time <6 minutes
        if entities.get('cecal_intubation_documented'):
            withdrawal_time = entities.get('withdrawal_time_minutes', 0)
            
            if withdrawal_time > 0 and withdrawal_time < 6:
                # FALSE POSITIVE: Procedure may have been incomplete/rushed
                corrected['false_positives_detected'].append({
                    'element': 'cecal_intubation',
                    'issue': f'Withdrawal time {withdrawal_time} min < 6 min threshold',
                    'risk': 'NCQA quality indicator suggests inadequate examination'
                })
                
                corrected['confidence_adjustments']['cecal_intubation_documented'] = {
                    'original': layer1.get('confidence_scores', {}).get('cecal_intubation_documented', 0),
                    'adjusted': 0.60,
                    'reason': 'Withdrawal time below quality threshold'
                }
        
        # Check 2: No cecal intubation but note mentions "poor prep"
        if not entities.get('cecal_intubation_documented'):
            note_lower = str(chart.get('clinical_note', '')).lower()
            
            if 'poor prep' in note_lower or 'inadequate' in note_lower:
                # TRUE NEGATIVE CONFIRMED: Procedure was indeed incomplete
                corrected['corrections_applied'].append({
                    'correction': 'Confirmed incomplete procedure due to poor preparation',
                    'reason': 'Clinical note documents inadequate bowel prep',
                    'severity': 'HIGH'
                })
                
                # Ensure marked as non-compliant
                corrected['final_compliant'] = False
                corrected['final_risk_level'] = 'CRITICAL'
        
        # Check 3: FIT test - check for result
        if chart.get('procedure_code') in ['82274', '3017F']:  # FIT codes
            if entities.get('result_documented'):
                # Good - FIT has result
                pass
            else:
                # FALSE POSITIVE: FIT ordered but no result
                corrected['false_positives_detected'].append({
                    'element': 'fit_completion',
                    'issue': 'FIT test code present but result not documented',
                    'risk': 'Ordered test without result does not meet numerator'
                })
                
                corrected['final_compliant'] = False
                corrected['final_risk_level'] = 'HIGH'
        
        return corrected
    
    def _correct_cbp(self, layer1: Dict, chart: pd.Series, layer2: Dict, corrected: Dict) -> Dict:
        """Self-correction for Controlling Blood Pressure - MOST CRITICAL"""
        
        entities = layer1.get('entities', {})
        methods = layer1.get('extraction_methods', {})
        
        # Check 1: CRITICAL - Both BP values present but from different sources
        if entities.get('systolic_bp') and entities.get('diastolic_bp'):
            sbp_method = methods.get('systolic_bp')
            dbp_method = methods.get('diastolic_bp')
            
            # If one from structured field and one from note extraction, they may be from different encounters
            if sbp_method != dbp_method:
                corrected['false_positives_detected'].append({
                    'element': 'bp_same_encounter',
                    'issue': f'SBP from {sbp_method}, DBP from {dbp_method} - likely different encounters',
                    'risk': 'CRITICAL: CMS requires both values from SAME encounter - #1 audit failure'
                })
                
                corrected['corrections_applied'].append({
                    'correction': 'Marked as non-compliant due to BP from different encounters',
                    'reason': 'NCQA requires both SBP and DBP from same encounter',
                    'severity': 'CRITICAL'
                })
                
                # FORCE non-compliant
                corrected['final_compliant'] = False
                corrected['final_risk_level'] = 'CRITICAL'
                corrected['final_compliance_score'] = 35
        
        # Check 2: Only one BP value present
        elif entities.get('systolic_bp') or entities.get('diastolic_bp'):
            # Confirm this is non-compliant (should already be, but double-check)
            missing_component = 'DBP' if entities.get('systolic_bp') else 'SBP'
            
            corrected['corrections_applied'].append({
                'correction': f'Confirmed non-compliant: Missing {missing_component}',
                'reason': f'Most common CBP audit failure (30% prevalence)',
                'severity': 'CRITICAL'
            })
            
            corrected['final_compliant'] = False
            corrected['final_risk_level'] = 'CRITICAL'
            corrected['final_compliance_score'] = 35
        
        # Check 3: BP values present but note says "home BP"
        if entities.get('systolic_bp') and entities.get('diastolic_bp'):
            note_lower = str(chart.get('clinical_note', '')).lower()
            
            if 'home bp' in note_lower or 'patient reports bp' in note_lower:
                # FALSE POSITIVE: Home BP doesn't count
                corrected['false_positives_detected'].append({
                    'element': 'bp_measurement_location',
                    'issue': 'BP appears to be patient-reported home reading',
                    'risk': 'Home BP readings do not meet NCQA criteria'
                })
                
                corrected['corrections_applied'].append({
                    'correction': 'Downgraded: Home BP does not count for HEDIS',
                    'reason': 'Office/clinic BP required per NCQA specifications',
                    'severity': 'CRITICAL'
                })
                
                corrected['final_compliant'] = False
                corrected['final_risk_level'] = 'CRITICAL'
        
        return corrected
    
    def _correct_cdc(self, layer1: Dict, chart: pd.Series, layer2: Dict, corrected: Dict) -> Dict:
        """Self-correction for Comprehensive Diabetes Care"""
        
        entities = layer1.get('entities', {})
        note_lower = str(chart.get('clinical_note', '')).lower()
        
        # Check 1: HbA1c procedure code but no value
        if chart.get('procedure_code') in ['83036', '83037', '3044F', '3045F', '3046F']:
            if not entities.get('hba1c_value'):
                # FALSE POSITIVE: Test ordered/coded but value not documented
                corrected['false_positives_detected'].append({
                    'element': 'hba1c_completion',
                    'issue': 'HbA1c code present but numeric value not documented',
                    'risk': 'CRITICAL: CMS requires actual result value, not just test code'
                })
                
                corrected['corrections_applied'].append({
                    'correction': 'Marked non-compliant: Missing HbA1c numeric value',
                    'reason': 'Test code alone insufficient - must have result percentage',
                    'severity': 'CRITICAL'
                })
                
                corrected['final_compliant'] = False
                corrected['final_risk_level'] = 'CRITICAL'
        
        # Check 2: Glucose value mentioned but not HbA1c
        if 'glucose' in note_lower and not entities.get('hba1c_value'):
            if 'fasting glucose' in note_lower or 'random glucose' in note_lower:
                # TRUE NEGATIVE CONFIRMED: Glucose is NOT the same as HbA1c
                corrected['corrections_applied'].append({
                    'correction': 'Confirmed non-compliant: Glucose test does not substitute for HbA1c',
                    'reason': 'Common confusion - glucose and HbA1c are different tests',
                    'severity': 'HIGH'
                })
                
                corrected['final_compliant'] = False
                corrected['final_risk_level'] = 'CRITICAL'
        
        # Check 3: Eye exam "mentioned" vs actually completed
        eye_exam_method = layer1.get('extraction_methods', {}).get('eye_exam_documented')
        if eye_exam_method == 'note_inference':
            # Check if note just says "eye exam recommended" vs "eye exam completed"
            if 'recommend' in note_lower or 'should' in note_lower or 'needs' in note_lower:
                # FALSE POSITIVE: Recommendation is not completion
                corrected['false_positives_detected'].append({
                    'element': 'eye_exam_completion',
                    'issue': 'Eye exam recommended but not documented as completed',
                    'risk': 'Recommendation does not meet completion requirement'
                })
                
                corrected['confidence_adjustments']['eye_exam_documented'] = {
                    'original': layer1.get('confidence_scores', {}).get('eye_exam_documented', 0),
                    'adjusted': 0.30,
                    'reason': 'Recommendation language suggests exam not yet done'
                }
        
        return corrected
    
    def _correct_ked(self, layer1: Dict, chart: pd.Series, layer2: Dict, corrected: Dict) -> Dict:
        """Self-correction for Kidney Health Evaluation"""
        
        entities = layer1.get('entities', {})
        
        # Check 1: Only one test documented when both required
        has_egfr = entities.get('egfr_value') or entities.get('egfr_documented')
        has_uacr = entities.get('uacr_documented')
        
        if has_egfr and not has_uacr:
            corrected['corrections_applied'].append({
                'correction': 'Confirmed non-compliant: Missing uACR despite having eGFR',
                'reason': 'KED requires BOTH tests - neither alone is sufficient',
                'severity': 'CRITICAL'
            })
            corrected['final_compliant'] = False
            corrected['final_risk_level'] = 'CRITICAL'
        
        elif has_uacr and not has_egfr:
            corrected['corrections_applied'].append({
                'correction': 'Confirmed non-compliant: Missing eGFR despite having uACR',
                'reason': 'KED requires BOTH tests - neither alone is sufficient',
                'severity': 'CRITICAL'
            })
            corrected['final_compliant'] = False
            corrected['final_risk_level'] = 'CRITICAL'
        
        return corrected
    
    def _recalculate_compliance(self, corrected: Dict, original_validation: Dict) -> Dict:
        """Recalculate final compliance score based on corrections"""
        
        # If we explicitly set compliance/risk in corrections, use those
        if 'final_compliant' in corrected and corrected['final_compliant'] != original_validation.get('compliant'):
            # Compliance changed - already set in corrections
            pass
        else:
            # No change - use original
            corrected['final_compliant'] = original_validation.get('compliant', False)
            corrected['final_risk_level'] = original_validation.get('risk_level', 'UNKNOWN')
            corrected['final_compliance_score'] = original_validation.get('compliance_score', 0)
        
        # Adjust compliance score based on false positives detected
        if corrected['false_positives_detected']:
            # Reduce score for each false positive
            reduction = len(corrected['false_positives_detected']) * 10
            corrected['final_compliance_score'] = max(0, corrected['final_compliance_score'] - reduction)
        
        # Increase score for false negatives corrected (we found something that was missed)
        if corrected['false_negatives_detected']:
            # But be conservative - only small increase
            increase = len(corrected['false_negatives_detected']) * 5
            corrected['final_compliance_score'] = min(100, corrected['final_compliance_score'] + increase)
        
        return corrected
    
    def get_performance_stats(self) -> Dict:
        """Calculate Layer 3 performance statistics"""
        
        if not self.processing_times:
            return {'error': 'No processing times recorded'}
        
        import statistics
        
        total_corrections = len(self.corrections_made)
        total_charts = len(self.processing_times)
        
        return {
            'total_charts_processed': total_charts,
            'total_corrections_made': total_corrections,
            'correction_rate': f"{(total_corrections/total_charts)*100:.1f}%" if total_charts > 0 else "0%",
            'average_time_ms': statistics.mean(self.processing_times),
            'median_time_ms': statistics.median(self.processing_times),
            'min_time_ms': min(self.processing_times),
            'max_time_ms': max(self.processing_times),
            'target_time_ms': 800,  # 0.8 seconds
            'meets_target': statistics.mean(self.processing_times) < 800,
            'corrections_by_measure': self._group_corrections_by_measure()
        }
    
    def _group_corrections_by_measure(self) -> Dict:
        """Group corrections by measure code"""
        
        by_measure = {}
        for correction in self.corrections_made:
            measure = correction['measure_code']
            if measure not in by_measure:
                by_measure[measure] = []
            by_measure[measure].append(correction)
        
        return {
            measure: {
                'count': len(corrections),
                'examples': corrections[:3]  # First 3 examples
            }
            for measure, corrections in by_measure.items()
        }


def main():
    """Test self-correction engine on validation results"""
    
    print("\n" + "=" * 70)
    print("AUDITSHIELD LIVE - LAYER 3: SELF-CORRECTION VALIDATION")
    print("Phase 2.2: Cross-Source Verification & Error Detection")
    print("=" * 70 + "\n")
    
    # Load data
    charts_df = pd.read_csv('/home/claude/chart_documentation.csv')
    validation_results_df = pd.read_csv('/home/claude/validation_results.csv')
    
    with open('/home/claude/layer1_extraction_results.json', 'r') as f:
        layer1_results = json.load(f)
    
    print(f"Processing {len(charts_df)} charts through Layer 3...")
    
    # Initialize engine
    engine = SelfCorrectionEngine()
    
    # Process all charts
    correction_results = []
    for idx, chart in charts_df.iterrows():
        # Get corresponding Layer 1 and Layer 2 results
        layer1_result = layer1_results[idx]
        layer2_result = validation_results_df.iloc[idx].to_dict()
        
        # Apply self-correction
        corrected = engine.validate_extraction(layer1_result, chart, layer2_result)
        correction_results.append(corrected)
        
        if (idx + 1) % 100 == 0:
            print(f"  Processed {idx + 1}/{len(charts_df)} charts...")
    
    print(f"  Processed {len(charts_df)}/{len(charts_df)} charts ✓")
    
    # Performance statistics
    perf_stats = engine.get_performance_stats()
    
    print("\n" + "=" * 70)
    print("LAYER 3 PROCESSING PERFORMANCE")
    print("=" * 70)
    print(f"Total Charts: {perf_stats['total_charts_processed']}")
    print(f"Corrections Made: {perf_stats['total_corrections_made']}")
    print(f"Correction Rate: {perf_stats['correction_rate']}")
    print(f"Average Processing Time: {perf_stats['average_time_ms']:.2f} ms")
    print(f"Median Processing Time: {perf_stats['median_time_ms']:.2f} ms")
    print(f"Target Time: {perf_stats['target_time_ms']} ms (0.8 seconds)")
    print(f"Meets Target: {'✓ YES' if perf_stats['meets_target'] else '✗ NO'}")
    
    # Correction breakdown
    print("\n" + "=" * 70)
    print("CORRECTIONS BY MEASURE")
    print("=" * 70)
    for measure, data in perf_stats['corrections_by_measure'].items():
        print(f"\n{measure}: {data['count']} corrections")
        for example in data['examples']:
            print(f"  • Chart {example['chart_id']}: {example['original_status']} → {example['final_status']}")
    
    # False positive/negative statistics
    total_false_positives = sum(len(r['false_positives_detected']) for r in correction_results)
    total_false_negatives = sum(len(r['false_negatives_detected']) for r in correction_results)
    
    print("\n" + "=" * 70)
    print("ERROR DETECTION SUMMARY")
    print("=" * 70)
    print(f"False Positives Detected: {total_false_positives}")
    print(f"False Negatives Detected: {total_false_negatives}")
    print(f"Total Errors Corrected: {total_false_positives + total_false_negatives}")
    
    # Save results
    print("\n" + "=" * 70)
    print("Saving Layer 3 correction results...")
    
    with open('/home/claude/layer3_correction_results.json', 'w') as f:
        json.dump(correction_results, f, indent=2)
    print("  ✓ layer3_correction_results.json")
    
    with open('/home/claude/layer3_performance.json', 'w') as f:
        json.dump(perf_stats, f, indent=2)
    print("  ✓ layer3_performance.json")
    
    print("\n" + "=" * 70)
    print("LAYER 3 SELF-CORRECTION - COMPLETE")
    print("=" * 70)
    print("\nNext: Integrate all 3 layers into compound validation pipeline")


if __name__ == "__main__":
    main()
