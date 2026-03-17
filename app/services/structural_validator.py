"""
Structural validation and compliance checking for CV analysis.
Adapts Risk Gate's structural logic to CV format validation.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re
from datetime import datetime

@dataclass
class ValidationIssue:
    """Represents a validation issue found in CV structure."""
    category: str
    severity: str  # 'critical', 'warning', 'info'
    message: str
    suggestion: str
    section: Optional[str] = None

@dataclass
class StructuralValidationResult:
    """Complete structural validation result."""
    is_complete: bool
    completeness_score: float
    critical_issues: List[ValidationIssue]
    warnings: List[ValidationIssue]
    suggestions: List[ValidationIssue]
    compliance_score: float
    industry_compliance: Dict[str, bool]

class StructuralValidator:
    """
    Validates CV structure and completeness using algorithmic analysis.
    Inspired by Risk Gate's structural logic approach.
    """

    def __init__(self):
        # Required sections for a complete CV
        self.required_sections = {
            'personal_details': ['name', 'contact'],
            'professional_summary': ['summary'],
            'experience': ['positions', 'dates'],
            'education': ['degrees'],
            'skills': ['technical_skills']
        }

        # Industry-specific requirements
        self.industry_requirements = {
            'technology': ['technical_skills', 'projects', 'certifications'],
            'finance': ['certifications', 'licenses', 'education'],
            'healthcare': ['licenses', 'certifications', 'education'],
            'legal': ['education', 'licenses', 'bar_admission'],
            'marketing': ['portfolio', 'campaigns', 'analytics']
        }

        # Common CV sections that should be present
        self.common_sections = [
            'personal_details', 'professional_summary', 'work_experience',
            'education', 'skills', 'certifications', 'projects', 'languages'
        ]

    def validate_cv_structure(self, structured_data: Dict[str, Any],
                            industry: Optional[str] = None) -> StructuralValidationResult:
        """
        Perform comprehensive structural validation of CV data.

        Args:
            structured_data: Parsed CV data from extraction
            industry: Target industry for compliance checking

        Returns:
            Complete validation result with issues and scores
        """
        critical_issues = []
        warnings = []
        suggestions = []

        # Check for missing required sections
        completeness_issues = self._check_completeness(structured_data)
        critical_issues.extend(completeness_issues['critical'])
        warnings.extend(completeness_issues['warnings'])

        # Validate section content quality
        content_issues = self._validate_content_quality(structured_data)
        warnings.extend(content_issues['warnings'])
        suggestions.extend(content_issues['suggestions'])

        # Check format consistency
        format_issues = self._validate_format_consistency(structured_data)
        warnings.extend(format_issues)

        # Industry-specific compliance
        compliance_result = self._check_industry_compliance(structured_data, industry)
        critical_issues.extend(compliance_result['critical'])
        warnings.extend(compliance_result['warnings'])

        # Calculate scores
        completeness_score = self._calculate_completeness_score(structured_data)
        compliance_score = self._calculate_compliance_score(structured_data, industry)

        # Overall completeness determination
        is_complete = len(critical_issues) == 0 and completeness_score >= 0.8

        return StructuralValidationResult(
            is_complete=is_complete,
            completeness_score=completeness_score,
            critical_issues=critical_issues,
            warnings=warnings,
            suggestions=suggestions,
            compliance_score=compliance_score,
            industry_compliance=compliance_result.get('compliance_status', {})
        )

    def _check_completeness(self, data: Dict[str, Any]) -> Dict[str, List[ValidationIssue]]:
        """Check if required sections are present and populated."""
        critical = []
        warnings = []

        # Check personal details
        if 'personal_details' not in data or not data.get('personal_details'):
            critical.append(ValidationIssue(
                category='completeness',
                severity='critical',
                message='Personal details section is missing',
                suggestion='Add a personal details section with name, contact information, and location',
                section='personal_details'
            ))
        else:
            personal = data['personal_details']
            if not personal.get('full_name'):
                critical.append(ValidationIssue(
                    category='completeness',
                    severity='critical',
                    message='Full name is missing from personal details',
                    suggestion='Add your full name at the top of the CV',
                    section='personal_details'
                ))
            if not any([personal.get('email'), personal.get('phone'), personal.get('location')]):
                warnings.append(ValidationIssue(
                    category='completeness',
                    severity='warning',
                    message='Contact information is incomplete',
                    suggestion='Add email, phone number, and location for better reachability',
                    section='personal_details'
                ))

        # Check professional summary
        if 'professional_summary' not in data or not data.get('professional_summary'):
            critical.append(ValidationIssue(
                category='completeness',
                severity='critical',
                message='Professional summary is missing',
                suggestion='Add a 2-3 sentence professional summary highlighting your key strengths and career goals',
                section='professional_summary'
            ))

        # Check work experience
        if 'professional_details' not in data or not data['professional_details'].get('experience'):
            critical.append(ValidationIssue(
                category='completeness',
                severity='critical',
                message='Work experience section is missing',
                suggestion='Add detailed work experience with company names, positions, dates, and achievements',
                section='experience'
            ))
        else:
            experience = data['professional_details']['experience']
            if len(experience) == 0:
                critical.append(ValidationIssue(
                    category='completeness',
                    severity='critical',
                    message='No work experience entries found',
                    suggestion='Add your work experience details including company, position, and duration',
                    section='experience'
                ))

        # Check education
        if 'education_details' not in data or not data['education_details'].get('education'):
            warnings.append(ValidationIssue(
                category='completeness',
                severity='warning',
                message='Education section is missing',
                suggestion='Add your educational background including degrees and institutions',
                section='education'
            ))

        # Check skills
        if 'professional_details' not in data or not data['professional_details'].get('skills'):
            warnings.append(ValidationIssue(
                category='completeness',
                severity='warning',
                message='Skills section is missing',
                suggestion='Add a skills section highlighting your technical and soft skills',
                section='skills'
            ))

        return {'critical': critical, 'warnings': warnings}

    def _validate_content_quality(self, data: Dict[str, Any]) -> Dict[str, List[ValidationIssue]]:
        """Validate the quality and completeness of section content."""
        warnings = []
        suggestions = []

        # Check professional summary length
        if 'professional_summary' in data and data['professional_summary']:
            summary = str(data['professional_summary'])
            word_count = len(summary.split())
            if word_count < 20:
                warnings.append(ValidationIssue(
                    category='content_quality',
                    severity='warning',
                    message='Professional summary is too brief',
                    suggestion='Expand your professional summary to 50-100 words highlighting your key achievements and career goals',
                    section='professional_summary'
                ))
            elif word_count > 150:
                suggestions.append(ValidationIssue(
                    category='content_quality',
                    severity='info',
                    message='Professional summary is quite long',
                    suggestion='Consider condensing to focus on the most impactful points',
                    section='professional_summary'
                ))

        # Check work experience detail
        if 'professional_details' in data and 'experience' in data['professional_details']:
            experience = data['professional_details']['experience']
            for i, exp in enumerate(experience):
                if isinstance(exp, dict):
                    # Check for achievements
                    description = exp.get('description', '')
                    if len(str(description).split()) < 10:
                        suggestions.append(ValidationIssue(
                            category='content_quality',
                            severity='info',
                            message=f'Work experience entry {i+1} lacks detail',
                            suggestion='Add specific achievements and responsibilities with quantifiable results',
                            section='experience'
                        ))

        # Check skills categorization
        if 'professional_details' in data and 'skills' in data['professional_details']:
            skills = data['professional_details']['skills']
            if isinstance(skills, list) and len(skills) > 0:
                # Check if skills are categorized
                has_categories = any(isinstance(skill, dict) and 'category' in skill for skill in skills)
                if not has_categories and len(skills) > 10:
                    suggestions.append(ValidationIssue(
                        category='content_quality',
                        severity='info',
                        message='Skills could be better organized',
                        suggestion='Group skills into categories like Technical Skills, Soft Skills, Tools & Technologies',
                        section='skills'
                    ))

        return {'warnings': warnings, 'suggestions': suggestions}

    def _validate_format_consistency(self, data: Dict[str, Any]) -> List[ValidationIssue]:
        """Check for format consistency issues."""
        issues = []

        # Check date formats in experience
        if 'professional_details' in data and 'experience' in data['professional_details']:
            experience = data['professional_details']['experience']
            date_pattern = re.compile(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2})\b')

            for i, exp in enumerate(experience):
                if isinstance(exp, dict):
                    start_date = exp.get('start_date', '')
                    end_date = exp.get('end_date', '')

                    if start_date and not date_pattern.search(str(start_date)):
                        issues.append(ValidationIssue(
                            category='format_consistency',
                            severity='warning',
                            message=f'Inconsistent date format in experience entry {i+1}',
                            suggestion='Use consistent date formats (e.g., MM/YYYY or Month YYYY)',
                            section='experience'
                        ))

        return issues

    def _check_industry_compliance(self, data: Dict[str, Any], industry: Optional[str]) -> Dict[str, Any]:
        """Check industry-specific compliance requirements."""
        critical = []
        warnings = []
        compliance_status = {}

        if not industry:
            return {'critical': critical, 'warnings': warnings, 'compliance_status': compliance_status}

        industry_reqs = self.industry_requirements.get(industry.lower(), [])

        for requirement in industry_reqs:
            compliant = False

            if requirement == 'technical_skills':
                skills = data.get('professional_details', {}).get('skills', [])
                if isinstance(skills, list) and len(skills) > 0:
                    # Check for technical skills
                    technical_indicators = ['programming', 'software', 'database', 'cloud', 'api', 'framework']
                    skill_text = ' '.join(str(skill).lower() for skill in skills)
                    compliant = any(indicator in skill_text for indicator in technical_indicators)
                compliance_status['technical_skills'] = compliant

            elif requirement == 'certifications':
                certs = data.get('education_details', {}).get('certifications', [])
                compliant = len(certs) > 0 if isinstance(certs, list) else bool(certs)
                compliance_status['certifications'] = compliant

            elif requirement == 'licenses':
                # Check for license-related content
                all_text = str(data).lower()
                license_indicators = ['license', 'certified', 'registered', 'accredited']
                compliant = any(indicator in all_text for indicator in license_indicators)
                compliance_status['licenses'] = compliant

            elif requirement == 'education':
                education = data.get('education_details', {}).get('education', [])
                compliant = len(education) > 0 if isinstance(education, list) else bool(education)
                compliance_status['education'] = compliant

            if not compliant:
                if requirement in ['licenses', 'certifications'] and industry in ['healthcare', 'legal', 'finance']:
                    critical.append(ValidationIssue(
                        category='industry_compliance',
                        severity='critical',
                        message=f'Missing required {requirement} for {industry} industry',
                        suggestion=f'Add relevant {requirement} required for {industry} positions',
                        section=requirement
                    ))
                else:
                    warnings.append(ValidationIssue(
                        category='industry_compliance',
                        severity='warning',
                        message=f'{requirement.replace("_", " ").title()} recommended for {industry} industry',
                        suggestion=f'Consider adding {requirement.replace("_", " ")} relevant to {industry} roles',
                        section=requirement
                    ))

        return {'critical': critical, 'warnings': warnings, 'compliance_status': compliance_status}

    def _calculate_completeness_score(self, data: Dict[str, Any]) -> float:
        """Calculate overall completeness score (0-1)."""
        sections_present = 0
        total_sections = len(self.common_sections)

        for section in self.common_sections:
            if section in data and data[section]:
                # Check if section has meaningful content
                if section == 'personal_details':
                    if data[section].get('full_name'):
                        sections_present += 1
                elif section == 'professional_details':
                    # Check sub-sections
                    prof_details = data[section]
                    if prof_details.get('experience') or prof_details.get('skills'):
                        sections_present += 1
                elif section == 'education_details':
                    if data[section].get('education'):
                        sections_present += 1
                else:
                    sections_present += 1

        return min(sections_present / total_sections, 1.0)

    def _calculate_compliance_score(self, data: Dict[str, Any], industry: Optional[str]) -> float:
        """Calculate industry compliance score (0-1)."""
        if not industry:
            return 1.0  # Neutral score if no industry specified

        compliance_status = self._check_industry_compliance(data, industry)['compliance_status']
        if not compliance_status:
            return 1.0

        compliant_items = sum(1 for status in compliance_status.values() if status)
        total_items = len(compliance_status)

        return compliant_items / total_items if total_items > 0 else 1.0
