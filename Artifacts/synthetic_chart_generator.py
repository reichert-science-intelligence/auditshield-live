"""
AuditShield Live - Synthetic HEDIS Chart Data Generator
Generates 411 realistic member charts with documentation gaps for CMS audit simulation

Author: Robert Hucks (Healthcare Data Scientist)
Purpose: Create test dataset for AuditShield Live mobile demo
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import random
from typing import Dict, List, Tuple

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

class HEDISChartGenerator:
    """Generate synthetic member charts with realistic HEDIS documentation patterns"""
    
    def __init__(self, num_members: int = 411):
        self.num_members = num_members
        self.measurement_year = 2026
        self.hedis_measures = [
            'BCS', 'COL', 'CBP', 'CDC', 'KED', 'OMW', 'BPD', 'SPD', 'FUH', 'HDO'
        ]
        
        # Realistic gap distribution based on industry patterns
        self.gap_distribution = {
            'complete': 0.68,      # 68% fully compliant
            'minor_gap': 0.22,     # 22% minor documentation gaps
            'major_gap': 0.10      # 10% major gaps requiring intervention
        }
        
    def generate_member_demographics(self) -> pd.DataFrame:
        """Generate realistic Medicare Advantage member demographics"""
        
        members = []
        for i in range(self.num_members):
            # Realistic age distribution for MA population (65-95)
            age = int(np.random.normal(75, 8))
            age = max(65, min(95, age))  # Clip to realistic range
            
            # Birth date calculation
            birth_year = self.measurement_year - age
            birth_date = datetime(birth_year, 
                                 random.randint(1, 12), 
                                 random.randint(1, 28))
            
            member = {
                'member_id': f'M{str(i+1).zfill(6)}',
                'age': age,
                'birth_date': birth_date.strftime('%Y-%m-%d'),
                'gender': random.choice(['M', 'F']),
                'state': random.choice(['PA', 'OH', 'WV', 'NY', 'MD']),
                'enrollment_months': random.randint(9, 12),  # Continuous enrollment
                'risk_score': round(random.uniform(0.8, 3.5), 2),  # HCC risk score
            }
            members.append(member)
        
        return pd.DataFrame(members)
    
    def assign_hedis_measures(self, demographics: pd.DataFrame) -> pd.DataFrame:
        """Assign HEDIS measures based on demographic eligibility"""
        
        measure_assignments = []
        
        for _, member in demographics.iterrows():
            # BCS (Breast Cancer Screening) - Women 50-74
            if member['gender'] == 'F' and 50 <= member['age'] <= 74:
                measure_assignments.append({
                    'member_id': member['member_id'],
                    'measure_code': 'BCS',
                    'measure_name': 'Breast Cancer Screening',
                    'eligible': True,
                    'denominator': True
                })
            
            # COL (Colorectal Cancer Screening) - All 50-75
            if 50 <= member['age'] <= 75:
                measure_assignments.append({
                    'member_id': member['member_id'],
                    'measure_code': 'COL',
                    'measure_name': 'Colorectal Cancer Screening',
                    'eligible': True,
                    'denominator': True
                })
            
            # CBP (Controlling Blood Pressure) - Age 18-85 with hypertension
            if 18 <= member['age'] <= 85 and random.random() < 0.45:  # 45% prevalence
                measure_assignments.append({
                    'member_id': member['member_id'],
                    'measure_code': 'CBP',
                    'measure_name': 'Controlling High Blood Pressure',
                    'eligible': True,
                    'denominator': True
                })
            
            # CDC (Diabetes Care) - Age 18-75 with diabetes
            if 18 <= member['age'] <= 75 and random.random() < 0.35:  # 35% prevalence
                measure_assignments.append({
                    'member_id': member['member_id'],
                    'measure_code': 'CDC',
                    'measure_name': 'Comprehensive Diabetes Care',
                    'eligible': True,
                    'denominator': True
                })
            
            # KED (Kidney Health Evaluation for Diabetics)
            if 18 <= member['age'] <= 75 and random.random() < 0.30:
                measure_assignments.append({
                    'member_id': member['member_id'],
                    'measure_code': 'KED',
                    'measure_name': 'Kidney Health Evaluation',
                    'eligible': True,
                    'denominator': True
                })
        
        return pd.DataFrame(measure_assignments)
    
    def generate_clinical_documentation(self, 
                                       member_id: str, 
                                       measure_code: str,
                                       gap_type: str) -> Dict:
        """Generate realistic clinical notes and procedure documentation"""
        
        # Base documentation templates by measure
        templates = {
            'BCS': {
                'complete': {
                    'procedure_code': '77067',
                    'procedure_name': 'Screening mammography, bilateral',
                    'service_date': self._random_date_in_year(),
                    'clinical_note': 'Patient presented for annual screening mammography. Bilateral views obtained. BI-RADS Category 1 - Negative findings. No masses, architectural distortion, or suspicious calcifications. Recommend routine annual screening.',
                    'ordering_provider': 'Dr. Sarah Chen, MD',
                    'performing_facility': 'Women\'s Imaging Center',
                    'result': 'NEGATIVE - BI-RADS 1'
                },
                'minor_gap': {
                    'procedure_code': '77067',
                    'procedure_name': 'Screening mammography',
                    'service_date': self._random_date_in_year(),
                    'clinical_note': 'Mammogram performed.',  # Insufficient detail
                    'ordering_provider': 'Dr. Chen',
                    'performing_facility': None,  # Missing facility
                    'result': 'Negative'
                },
                'major_gap': {
                    'procedure_code': None,  # Missing procedure code
                    'procedure_name': 'Breast imaging',
                    'service_date': self._random_date_in_year(),
                    'clinical_note': 'Patient discussed breast health. Screening recommended.',  # No proof of completion
                    'ordering_provider': 'Dr. Chen',
                    'performing_facility': None,
                    'result': None
                }
            },
            'COL': {
                'complete': {
                    'procedure_code': 'G0121',
                    'procedure_name': 'Screening colonoscopy',
                    'service_date': self._random_date_in_range(days_back=365*3),  # Within 10 years
                    'clinical_note': 'Colonoscopy performed under conscious sedation. Cecum intubated, withdrawal time 12 minutes. Entire colon visualized. Two small polyps (<5mm) in sigmoid colon, removed with cold forceps. Pathology: benign hyperplastic polyps. Recommend repeat in 5-10 years.',
                    'ordering_provider': 'Dr. James Martinez, MD',
                    'performing_facility': 'Gastroenterology Associates',
                    'result': 'COMPLETE - Cecal intubation achieved'
                },
                'minor_gap': {
                    'procedure_code': 'G0105',
                    'procedure_name': 'Colorectal cancer screening',
                    'service_date': self._random_date_in_range(days_back=365*3),
                    'clinical_note': 'Colonoscopy attempted. Poor prep quality.',  # Incomplete procedure
                    'ordering_provider': 'Dr. Martinez',
                    'performing_facility': 'GI Associates',
                    'result': None  # Missing completion status
                },
                'major_gap': {
                    'procedure_code': None,
                    'procedure_name': 'FIT test discussed',
                    'service_date': self._random_date_in_year(),
                    'clinical_note': 'Patient counseled on colorectal cancer screening options. Patient to obtain FIT kit.',
                    'ordering_provider': 'Dr. Martinez',
                    'performing_facility': None,
                    'result': None  # No test completed
                }
            },
            'CBP': {
                'complete': {
                    'procedure_code': '99213',
                    'procedure_name': 'Office visit - BP management',
                    'service_date': self._random_date_in_year(),
                    'clinical_note': 'Patient seen for HTN management. BP today: 128/76 mmHg (seated, left arm, appropriate cuff size). Patient reports medication compliance. Diet and exercise reviewed. Continue current antihypertensive regimen.',
                    'systolic_bp': 128,
                    'diastolic_bp': 76,
                    'bp_controlled': True,
                    'ordering_provider': 'Dr. Emily Roberts, MD'
                },
                'minor_gap': {
                    'procedure_code': '99213',
                    'procedure_name': 'Office visit',
                    'service_date': self._random_date_in_year(),
                    'clinical_note': 'BP: 132/78. Patient feeling well.',  # Missing both SBP and DBP readings
                    'systolic_bp': 132,
                    'diastolic_bp': None,  # Missing DBP
                    'bp_controlled': None,
                    'ordering_provider': 'Dr. Roberts'
                },
                'major_gap': {
                    'procedure_code': '99213',
                    'procedure_name': 'Follow-up visit',
                    'service_date': self._random_date_in_year(),
                    'clinical_note': 'Patient reports BP "good at home". Continue meds.',  # No actual BP measurement
                    'systolic_bp': None,
                    'diastolic_bp': None,
                    'bp_controlled': None,
                    'ordering_provider': 'Dr. Roberts'
                }
            },
            'CDC': {
                'complete': {
                    'procedure_code': '83036',
                    'procedure_name': 'HbA1c measurement',
                    'service_date': self._random_date_in_year(),
                    'clinical_note': 'Diabetes follow-up. HbA1c today: 7.2% (goal <8%). Patient reports good glucose control at home (avg 140 mg/dL). Retinal exam scheduled. Microalbumin ordered. Continue metformin 1000mg BID.',
                    'hba1c_value': 7.2,
                    'hba1c_controlled': True,
                    'eye_exam_completed': True,
                    'nephropathy_screening': True,
                    'ordering_provider': 'Dr. Michael Thompson, MD'
                },
                'minor_gap': {
                    'procedure_code': '83036',
                    'procedure_name': 'HbA1c',
                    'service_date': self._random_date_in_year(),
                    'clinical_note': 'A1c checked. Patient counseled on diabetes management.',  # Missing actual value
                    'hba1c_value': None,  # Value not documented
                    'hba1c_controlled': None,
                    'eye_exam_completed': False,
                    'nephropathy_screening': False,
                    'ordering_provider': 'Dr. Thompson'
                },
                'major_gap': {
                    'procedure_code': None,
                    'procedure_name': 'Diabetes visit',
                    'service_date': self._random_date_in_year(),
                    'clinical_note': 'Patient reports diabetes "under control". Continue current medications.',
                    'hba1c_value': None,
                    'hba1c_controlled': None,
                    'eye_exam_completed': False,
                    'nephropathy_screening': False,
                    'ordering_provider': 'Dr. Thompson'
                }
            }
        }
        
        # Return appropriate template based on gap type
        if measure_code in templates:
            return templates[measure_code].get(gap_type, templates[measure_code]['complete'])
        else:
            # Default template for other measures
            return {
                'procedure_code': 'XXXXX',
                'service_date': self._random_date_in_year(),
                'clinical_note': f'Documentation for {measure_code} measure.',
                'ordering_provider': 'Dr. Provider Name'
            }
    
    def _random_date_in_year(self) -> str:
        """Generate random date within measurement year"""
        start_date = datetime(self.measurement_year - 1, 1, 1)
        end_date = datetime(self.measurement_year - 1, 12, 31)
        days_between = (end_date - start_date).days
        random_days = random.randint(0, days_between)
        random_date = start_date + timedelta(days=random_days)
        return random_date.strftime('%Y-%m-%d')
    
    def _random_date_in_range(self, days_back: int = 365) -> str:
        """Generate random date within specified days back from measurement year"""
        end_date = datetime(self.measurement_year - 1, 12, 31)
        start_date = end_date - timedelta(days=days_back)
        days_between = (end_date - start_date).days
        random_days = random.randint(0, days_between)
        random_date = start_date + timedelta(days=random_days)
        return random_date.strftime('%Y-%m-%d')
    
    def calculate_audit_risk_score(self, documentation: Dict, gap_type: str) -> Tuple[int, str, float]:
        """Calculate audit failure risk based on documentation completeness"""
        
        risk_scores = {
            'complete': (95, 'LOW', 0.05),  # 95% compliance, 5% failure probability
            'minor_gap': (72, 'MEDIUM', 0.28),  # 72% compliance, 28% failure probability  
            'major_gap': (35, 'CRITICAL', 0.85)  # 35% compliance, 85% failure probability
        }
        
        compliance_score, risk_level, failure_prob = risk_scores.get(
            gap_type, 
            (50, 'HIGH', 0.50)
        )
        
        return compliance_score, risk_level, failure_prob
    
    def calculate_star_rating_impact(self, 
                                     measure_code: str, 
                                     failure_probability: float,
                                     total_denominator: int = 411) -> float:
        """Calculate projected Star Rating point loss if measure fails audit"""
        
        # Star Rating weights by measure (approximate)
        measure_weights = {
            'BCS': 3.0,  # High weight (preventive care)
            'COL': 3.0,  # High weight (preventive care)
            'CBP': 3.0,  # High weight (outcomes)
            'CDC': 3.0,  # High weight (diabetes management)
            'KED': 1.0,  # Lower weight
            'OMW': 1.0,
            'BPD': 1.0,
            'SPD': 1.0,
            'FUH': 1.0,
            'HDO': 1.0
        }
        
        weight = measure_weights.get(measure_code, 1.0)
        
        # Impact calculation: (failure_probability) × (measure_weight) × (performance_gap)
        # Assuming each failed chart reduces measure performance by ~0.24% (1/411)
        performance_impact = (1 / total_denominator) * 100  # % impact per chart
        star_impact = failure_probability * weight * (performance_impact / 100)
        
        return round(star_impact, 4)
    
    def generate_complete_dataset(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Generate complete synthetic dataset with all components"""
        
        print("Generating member demographics...")
        demographics = self.generate_member_demographics()
        
        print("Assigning HEDIS measures...")
        measure_assignments = self.assign_hedis_measures(demographics)
        
        print("Generating clinical documentation with realistic gaps...")
        chart_details = []
        
        # Ensure we get exactly 411 charts with realistic distribution
        total_charts = len(measure_assignments)
        
        # Calculate how many of each gap type
        num_complete = int(total_charts * self.gap_distribution['complete'])
        num_minor = int(total_charts * self.gap_distribution['minor_gap'])
        num_major = total_charts - num_complete - num_minor
        
        # Create gap type list
        gap_types = (['complete'] * num_complete + 
                     ['minor_gap'] * num_minor + 
                     ['major_gap'] * num_major)
        random.shuffle(gap_types)
        
        for idx, (_, measure) in enumerate(measure_assignments.iterrows()):
            gap_type = gap_types[idx]
            
            # Generate clinical documentation
            clinical_doc = self.generate_clinical_documentation(
                measure['member_id'],
                measure['measure_code'],
                gap_type
            )
            
            # Calculate risk metrics
            compliance_score, risk_level, failure_prob = self.calculate_audit_risk_score(
                clinical_doc, 
                gap_type
            )
            
            star_impact = self.calculate_star_rating_impact(
                measure['measure_code'],
                failure_prob,
                total_charts
            )
            
            chart_detail = {
                'chart_id': f"C{str(idx+1).zfill(6)}",
                'member_id': measure['member_id'],
                'measure_code': measure['measure_code'],
                'measure_name': measure['measure_name'],
                'gap_type': gap_type,
                'compliance_score': compliance_score,
                'risk_level': risk_level,
                'audit_failure_probability': failure_prob,
                'star_rating_impact': star_impact,
                **clinical_doc
            }
            
            chart_details.append(chart_detail)
        
        chart_df = pd.DataFrame(chart_details)
        
        # Summary statistics
        print("\n" + "="*60)
        print("SYNTHETIC DATASET GENERATION COMPLETE")
        print("="*60)
        print(f"Total Members: {len(demographics)}")
        print(f"Total Charts: {len(chart_df)}")
        print(f"\nGap Distribution:")
        print(f"  Complete (Audit-Ready): {len(chart_df[chart_df['gap_type']=='complete'])} ({len(chart_df[chart_df['gap_type']=='complete'])/len(chart_df)*100:.1f}%)")
        print(f"  Minor Gaps: {len(chart_df[chart_df['gap_type']=='minor_gap'])} ({len(chart_df[chart_df['gap_type']=='minor_gap'])/len(chart_df)*100:.1f}%)")
        print(f"  Major Gaps: {len(chart_df[chart_df['gap_type']=='major_gap'])} ({len(chart_df[chart_df['gap_type']=='major_gap'])/len(chart_df)*100:.1f}%)")
        print(f"\nRisk Level Distribution:")
        for level in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']:
            count = len(chart_df[chart_df['risk_level']==level])
            if count > 0:
                print(f"  {level}: {count} charts ({count/len(chart_df)*100:.1f}%)")
        print(f"\nMeasure Distribution:")
        for measure in chart_df['measure_code'].value_counts().head(5).items():
            print(f"  {measure[0]}: {measure[1]} charts")
        
        return demographics, measure_assignments, chart_df


def main():
    """Generate and save synthetic HEDIS chart dataset"""
    
    print("AuditShield Live - Synthetic Chart Generator")
    print("=" * 60)
    
    # Initialize generator
    generator = HEDISChartGenerator(num_members=411)
    
    # Generate complete dataset
    demographics, measures, charts = generator.generate_complete_dataset()
    
    # Save to CSV files
    print("\nSaving datasets to CSV files...")
    demographics.to_csv('/home/claude/member_demographics.csv', index=False)
    measures.to_csv('/home/claude/measure_assignments.csv', index=False)
    charts.to_csv('/home/claude/chart_documentation.csv', index=False)
    
    # Create JSON version for mobile app
    print("Creating JSON format for mobile app...")
    
    # Create hierarchical structure for mobile app
    mobile_data = {
        'metadata': {
            'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'measurement_year': 2026,
            'total_members': len(demographics),
            'total_charts': len(charts),
            'audit_deadline_days': 60
        },
        'summary_stats': {
            'compliance_rate': f"{len(charts[charts['gap_type']=='complete'])/len(charts)*100:.1f}%",
            'charts_at_risk': len(charts[charts['risk_level'].isin(['HIGH', 'CRITICAL'])]),
            'projected_star_impact': round(charts['star_rating_impact'].sum(), 2),
            'risk_distribution': {
                'critical': len(charts[charts['risk_level']=='CRITICAL']),
                'high': len(charts[charts['risk_level']=='HIGH']),
                'medium': len(charts[charts['risk_level']=='MEDIUM']),
                'low': len(charts[charts['risk_level']=='LOW'])
            }
        },
        'charts': charts.to_dict('records')
    }
    
    with open('/home/claude/auditshield_mobile_data.json', 'w') as f:
        json.dump(mobile_data, f, indent=2)
    
    print("\n" + "="*60)
    print("FILES GENERATED:")
    print("="*60)
    print("1. member_demographics.csv - Member demographic data")
    print("2. measure_assignments.csv - HEDIS measure eligibility")
    print("3. chart_documentation.csv - Complete chart details with gaps")
    print("4. auditshield_mobile_data.json - Mobile app ready format")
    print("\nReady for Phase 1.2: NCQA Specification Database")


if __name__ == "__main__":
    main()
