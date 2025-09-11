#!/usr/bin/env python3
"""
FAIR Compliance Checker for Psycho-Validator
Evaluates datasets against FAIR principles and provides recommendations
"""

import json
import os
import re
from pathlib import Path

class FAIRComplianceChecker:
    def __init__(self):
        self.score = {
            'findable': 0,
            'accessible': 0, 
            'interoperable': 0,
            'reusable': 0
        }
        self.max_scores = {
            'findable': 25,
            'accessible': 25,
            'interoperable': 25, 
            'reusable': 25
        }
        self.recommendations = []
    
    def check_findable(self, metadata):
        """Check Findable criteria"""
        score = 0
        
        # F1: Unique identifier
        if metadata.get('Metadata', {}).get('DatasetDOI'):
            score += 5
            self.recommendations.append("✅ Dataset has DOI for unique identification")
        else:
            self.recommendations.append("❌ Add DOI to Metadata.DatasetDOI for unique identification")
        
        # F2: Rich metadata
        required_fields = ['Creator', 'CreationDate', 'SchemaVersion']
        missing_fields = [f for f in required_fields if not metadata.get('Metadata', {}).get(f)]
        
        if not missing_fields:
            score += 5
            self.recommendations.append("✅ All required metadata fields present")
        else:
            self.recommendations.append(f"❌ Missing required metadata: {', '.join(missing_fields)}")
        
        # F3: Keywords and descriptions
        keywords = metadata.get('Metadata', {}).get('Keywords', [])
        if keywords and len(keywords) >= 3:
            score += 5
            self.recommendations.append(f"✅ Good keyword coverage ({len(keywords)} keywords)")
        else:
            self.recommendations.append("❌ Add at least 3 keywords for better discoverability")
        
        # F4: ORCID identification
        if metadata.get('Metadata', {}).get('CreatorORCID'):
            score += 5
            self.recommendations.append("✅ Creator has ORCID identifier")
        else:
            self.recommendations.append("❌ Add CreatorORCID for researcher identification")
        
        # F5: Institutional affiliation
        if metadata.get('Metadata', {}).get('InstitutionROR'):
            score += 5
            self.recommendations.append("✅ Institution has ROR identifier")
        else:
            self.recommendations.append("❌ Add InstitutionROR for institutional identification")
        
        return score
    
    def check_accessible(self, metadata, file_path):
        """Check Accessible criteria"""
        score = 0
        
        # A1: Clear license
        license_info = metadata.get('Metadata', {}).get('License')
        if license_info and license_info != 'All rights reserved':
            score += 8
            self.recommendations.append(f"✅ Clear license specified: {license_info}")
        else:
            self.recommendations.append("❌ Specify clear usage license (e.g., CC-BY, CC0)")
        
        # A2: Standard file format
        file_format = metadata.get('Technical', {}).get('FileFormat', '').lower()
        standard_formats = ['json', 'tsv', 'csv', 'png', 'jpg', 'wav', 'mp3', 'edf']
        
        if file_format in standard_formats:
            score += 5
            self.recommendations.append(f"✅ Using standard format: {file_format}")
        else:
            self.recommendations.append("❌ Consider using more standard file formats")
        
        # A3: File accessibility
        if os.path.exists(file_path):
            score += 4
            self.recommendations.append("✅ Data file is accessible")
        else:
            self.recommendations.append("❌ Data file not found or not accessible")
        
        # A4: Documentation completeness
        description = metadata.get('Metadata', {}).get('Description')
        if description and len(description) > 50:
            score += 4
            self.recommendations.append("✅ Comprehensive description provided")
        else:
            self.recommendations.append("❌ Add detailed description (>50 characters)")
        
        # A5: Contact information
        creator = metadata.get('Metadata', {}).get('Creator')
        if creator and '@' in creator:  # Basic email check
            score += 4
            self.recommendations.append("✅ Contact information available")
        else:
            self.recommendations.append("❌ Include contact information in Creator field")
        
        return score
    
    def check_interoperable(self, metadata):
        """Check Interoperable criteria"""
        score = 0
        
        # I1: Schema compliance
        schema_version = metadata.get('Metadata', {}).get('SchemaVersion')
        if schema_version and re.match(r'^\d+\.\d+\.\d+$', schema_version):
            score += 8
            self.recommendations.append(f"✅ Valid schema version: {schema_version}")
        else:
            self.recommendations.append("❌ Use semantic versioning for schema compliance")
        
        # I2: Controlled vocabulary
        categories = metadata.get('Categories', {})
        if categories and len(categories) >= 2:
            score += 5
            self.recommendations.append("✅ Using controlled vocabulary in categories")
        else:
            self.recommendations.append("❌ Use more structured categories for interoperability")
        
        # I3: Standard identifiers
        study_fields = metadata.get('Study', {})
        bids_pattern = r'^(sub-\d+|ses-\w+|run-\d+|task-\w+)$'
        
        bids_compliance = 0
        for field, value in study_fields.items():
            if field in ['Subject', 'Session', 'Run', 'Task'] and isinstance(value, str):
                if re.match(bids_pattern, value) or field == 'Task':
                    bids_compliance += 1
        
        if bids_compliance >= 2:
            score += 6
            self.recommendations.append(f"✅ Good BIDS compliance ({bids_compliance} fields)")
        else:
            self.recommendations.append("❌ Improve BIDS naming convention compliance")
        
        # I4: Linked data principles
        related_pubs = metadata.get('Metadata', {}).get('RelatedPublications', [])
        if related_pubs:
            score += 6
            self.recommendations.append(f"✅ Linked to publications ({len(related_pubs)} DOIs)")
        else:
            self.recommendations.append("❌ Link to related publications via DOI")
        
        return score
    
    def check_reusable(self, metadata):
        """Check Reusable criteria"""
        score = 0
        
        # R1: Rich provenance
        technical_fields = metadata.get('Technical', {})
        required_technical = ['StimulusType', 'FileFormat']
        
        if all(field in technical_fields for field in required_technical):
            score += 8
            self.recommendations.append("✅ Complete technical specifications")
        else:
            missing = [f for f in required_technical if f not in technical_fields]
            self.recommendations.append(f"❌ Missing technical fields: {', '.join(missing)}")
        
        # R2: Usage guidelines
        license_info = metadata.get('Metadata', {}).get('License', '')
        if license_info.startswith('CC') or 'open' in license_info.lower():
            score += 5
            self.recommendations.append("✅ Open license promotes reuse")
        else:
            self.recommendations.append("❌ Consider more open licensing for better reusability")
        
        # R3: Domain standards
        study_domain = metadata.get('Categories', {}).get('StudyDomain')
        if study_domain:
            score += 4
            self.recommendations.append(f"✅ Clear domain classification: {study_domain}")
        else:
            self.recommendations.append("❌ Specify StudyDomain for context")
        
        # R4: Quality metrics
        data_quality = metadata.get('Categories', {}).get('DataQuality')
        if data_quality:
            score += 4
            self.recommendations.append(f"✅ Data quality assessed: {data_quality}")
        else:
            self.recommendations.append("❌ Include data quality assessment")
        
        # R5: Versioning and updates
        creation_date = metadata.get('Metadata', {}).get('CreationDate')
        if creation_date and re.match(r'^\d{4}-\d{2}-\d{2}$', creation_date):
            score += 4
            self.recommendations.append("✅ Clear temporal information")
        else:
            self.recommendations.append("❌ Use ISO date format (YYYY-MM-DD)")
        
        return score
    
    def evaluate_dataset(self, metadata_file):
        """Evaluate complete FAIR compliance"""
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
        except Exception as e:
            return {"error": f"Could not load metadata: {e}"}
        
        # Get corresponding data file
        data_file = metadata_file.replace('.json', '').replace('_stim', '')
        
        # Run all FAIR checks
        self.score['findable'] = self.check_findable(metadata)
        self.score['accessible'] = self.check_accessible(metadata, data_file)
        self.score['interoperable'] = self.check_interoperable(metadata)
        self.score['reusable'] = self.check_reusable(metadata)
        
        # Calculate percentages
        percentages = {}
        for category, score in self.score.items():
            percentages[category] = (score / self.max_scores[category]) * 100
        
        total_percentage = sum(percentages.values()) / 4
        
        return {
            'scores': self.score,
            'percentages': percentages,
            'total_percentage': total_percentage,
            'recommendations': self.recommendations,
            'grade': self.get_grade(total_percentage)
        }
    
    def get_grade(self, percentage):
        """Convert percentage to letter grade"""
        if percentage >= 90:
            return "A - Excellent FAIR compliance"
        elif percentage >= 80:
            return "B - Good FAIR compliance"
        elif percentage >= 70:
            return "C - Acceptable FAIR compliance"
        elif percentage >= 60:
            return "D - Poor FAIR compliance"
        else:
            return "F - Inadequate FAIR compliance"

def main():
    """Command line FAIR compliance checker"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python fair_checker.py <metadata_file.json>")
        sys.exit(1)
    
    metadata_file = sys.argv[1]
    
    if not os.path.exists(metadata_file):
        print(f"Error: File {metadata_file} not found")
        sys.exit(1)
    
    checker = FAIRComplianceChecker()
    results = checker.evaluate_dataset(metadata_file)
    
    if 'error' in results:
        print(f"❌ {results['error']}")
        sys.exit(1)
    
    # Display results
    print(f"\n🔍 FAIR Compliance Report: {os.path.basename(metadata_file)}")
    print("=" * 60)
    
    # Overall grade
    print(f"🎯 Overall Grade: {results['grade']}")
    print(f"📊 Total Score: {results['total_percentage']:.1f}%\n")
    
    # Individual scores
    print("📈 Category Scores:")
    for category, percentage in results['percentages'].items():
        bar_length = int(percentage / 5)  # Scale to 20 chars max
        bar = "█" * bar_length + "░" * (20 - bar_length)
        print(f"  {category.upper():13} [{bar}] {percentage:5.1f}%")
    
    # Recommendations
    print(f"\n💡 Recommendations ({len(results['recommendations'])} items):")
    for i, rec in enumerate(results['recommendations'], 1):
        print(f"  {i:2d}. {rec}")
    
    # Exit with appropriate code
    sys.exit(0 if results['total_percentage'] >= 70 else 1)

if __name__ == "__main__":
    main()
