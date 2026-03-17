"""
Risk assessment and scoring system for CV analysis.
Adapts Risk Gate's risk scoring approach to CV evaluation.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import math

class RiskLevel(Enum):
    """Risk assessment levels for CV analysis."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ComplianceStatus(Enum):
    """Compliance status for different criteria."""
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"

@dataclass
class RiskFactor:
    """Represents a risk factor in CV evaluation."""
    name: str
    weight: float  # 0-1, importance of this factor
    score: float   # 0-1, actual performance
    threshold: float  # minimum acceptable score
    description: str
    category: str

@dataclass
class RiskAssessment:
    """Complete risk assessment result."""
    overall_score: float  # 0-100
    risk_level: RiskLevel
    risk_factors: List[RiskFactor]
    critical_issues: List[str]
    warnings: List[str]
    recommendations: List[str]
    compliance_status: Dict[str, ComplianceStatus]
    industry_score: float
    completeness_score: float

class CVRiskAssessor:
    """
    Comprehensive risk assessment system for CV analysis.
    Inspired by Risk Gate's multi-factor risk evaluation approach.
    """

    def __init__(self):
        # Define risk factors with weights and thresholds
        self.risk_factors = {
            'completeness': RiskFactor(
                name='CV Completeness',
                weight=0.25,
                score=0.0,
                threshold=0.7,
                description='Overall completeness of CV sections',
                category='structure'
            ),
            'content_quality': RiskFactor(
                name='Content Quality',
                weight=0.20,
                score=0.0,
                threshold=0.6,
                description='Quality and detail of content',
                category='content'
            ),
            'skills_relevance': RiskFactor(
                name='Skills Relevance',
                weight=0.20,
                score=0.0,
                threshold=0.5,
                description='Relevance of skills to target role',
                category='relevance'
            ),
            'experience_depth': RiskFactor(
                name='Experience Depth',
                weight=0.15,
                score=0.0,
                threshold=0.6,
                description='Depth and quality of work experience',
                category='experience'
            ),
            'industry_compliance': RiskFactor(
                name='Industry Compliance',
                weight=0.10,
                score=0.0,
                threshold=0.7,
                description='Compliance with industry standards',
                category='compliance'
            ),
            'format_consistency': RiskFactor(
                name='Format Consistency',
                weight=0.10,
                score=0.0,
                threshold=0.8,
                description='Consistency in formatting and presentation',
                category='presentation'
            )
        }

    def assess_cv_risks(self, analysis_result: Dict[str, Any],
                       job_requirements: Dict[str, Any],
                       industry: Optional[str] = None) -> RiskAssessment:
        """
        Perform comprehensive risk assessment of CV analysis results.

        Args:
            analysis_result: Complete CV analysis result
            job_requirements: Target job requirements
            industry: Target industry

        Returns:
            Complete risk assessment
        """
        # Extract relevant data from analysis result
        structured_data = analysis_result.get('structured_data', {})
        match_analysis = analysis_result.get('match_analysis', {})
        extraction_metadata = analysis_result.get('extraction_metadata', {})

        # Calculate individual risk factor scores
        self._calculate_completeness_risk(structured_data)
        self._calculate_content_quality_risk(structured_data, extraction_metadata)
        self._calculate_skills_relevance_risk(structured_data, job_requirements)
        self._calculate_experience_depth_risk(structured_data)
        self._calculate_industry_compliance_risk(structured_data, industry)
        self._calculate_format_consistency_risk(structured_data)

        # Calculate overall score
        overall_score = self._calculate_overall_score()

        # Determine risk level
        risk_level = self._determine_risk_level(overall_score)

        # Generate issues and recommendations
        critical_issues, warnings, recommendations = self._generate_feedback()

        # Compliance status
        compliance_status = self._assess_compliance_status()

        # Industry and completeness scores
        industry_score = self.risk_factors['industry_compliance'].score
        completeness_score = self.risk_factors['completeness'].score

        return RiskAssessment(
            overall_score=overall_score,
            risk_level=risk_level,
            risk_factors=list(self.risk_factors.values()),
            critical_issues=critical_issues,
            warnings=warnings,
            recommendations=recommendations,
            compliance_status=compliance_status,
            industry_score=industry_score,
            completeness_score=completeness_score
        )

    def _calculate_completeness_risk(self, structured_data: Dict[str, Any]):
        """Calculate completeness risk factor."""
        required_sections = ['personal_details', 'professional_details', 'education_details']
        present_sections = 0

        for section in required_sections:
            if section in structured_data and structured_data[section]:
                if section == 'personal_details':
                    # Check for essential personal info
                    personal = structured_data[section]
                    if personal.get('full_name') and (personal.get('email') or personal.get('phone')):
                        present_sections += 1
                elif section == 'professional_details':
                    # Check for experience and skills
                    prof = structured_data[section]
                    if (prof.get('experience') and len(prof['experience']) > 0) or prof.get('skills'):
                        present_sections += 1
                elif section == 'education_details':
                    # Check for education info
                    edu = structured_data[section]
                    if edu.get('education') or edu.get('certifications'):
                        present_sections += 1
                else:
                    present_sections += 1

        completeness_score = present_sections / len(required_sections)
        self.risk_factors['completeness'].score = min(completeness_score, 1.0)

    def _calculate_content_quality_risk(self, structured_data: Dict[str, Any],
                                       extraction_metadata: Dict[str, Any]):
        """Calculate content quality risk factor."""
        quality_indicators = []
        total_indicators = 4

        # Check summary length
        summary = structured_data.get('professional_summary', '')
        if len(str(summary).split()) >= 30:  # Decent summary length
            quality_indicators.append(1)
        elif len(str(summary).split()) >= 10:
            quality_indicators.append(0.5)

        # Check experience detail
        experience = structured_data.get('professional_details', {}).get('experience', [])
        detailed_experience = 0
        for exp in experience:
            if isinstance(exp, dict) and len(str(exp.get('description', '')).split()) >= 20:
                detailed_experience += 1

        if len(experience) > 0:
            detail_ratio = detailed_experience / len(experience)
            quality_indicators.append(min(detail_ratio, 1.0))

        # Check skills count and variety
        skills = structured_data.get('professional_details', {}).get('skills', [])
        if isinstance(skills, list):
            if len(skills) >= 5:
                quality_indicators.append(1.0)
            elif len(skills) >= 3:
                quality_indicators.append(0.5)

        # Check extraction quality
        extraction_method = extraction_metadata.get('method', '')
        if extraction_method in ['pdfplumber', 'pymupdf']:
            quality_indicators.append(1.0)  # High quality extraction
        elif extraction_method == 'ocr':
            quality_indicators.append(0.7)  # OCR might have errors

        quality_score = sum(quality_indicators) / total_indicators if quality_indicators else 0
        self.risk_factors['content_quality'].score = min(quality_score, 1.0)

    def _calculate_skills_relevance_risk(self, structured_data: Dict[str, Any],
                                        job_requirements: Dict[str, Any]):
        """Calculate skills relevance risk factor."""
        cv_skills = set()
        job_skills = set()

        # Extract CV skills
        skills_data = structured_data.get('professional_details', {}).get('skills', [])
        if isinstance(skills_data, list):
            for skill in skills_data:
                if isinstance(skill, str):
                    cv_skills.add(skill.lower())
                elif isinstance(skill, dict):
                    skill_name = skill.get('name', skill.get('skill', ''))
                    cv_skills.add(str(skill_name).lower())

        # Extract job skills from requirements
        job_skills_data = job_requirements.get('required_skills', [])
        if isinstance(job_skills_data, list):
            for skill in job_skills_data:
                if isinstance(skill, str):
                    job_skills.add(skill.lower())
                elif isinstance(skill, dict):
                    skill_name = skill.get('name', skill.get('skill', ''))
                    job_skills.add(str(skill_name).lower())

        if not job_skills:
            # If no job skills specified, assume neutral relevance
            self.risk_factors['skills_relevance'].score = 0.7
            return

        # Calculate relevance score
        matching_skills = cv_skills.intersection(job_skills)
        relevance_score = len(matching_skills) / len(job_skills) if job_skills else 0

        # Bonus for having more skills than required
        coverage_bonus = min(len(cv_skills) / len(job_skills), 2.0) if job_skills else 1.0
        final_score = min(relevance_score * coverage_bonus, 1.0)

        self.risk_factors['skills_relevance'].score = final_score

    def _calculate_experience_depth_risk(self, structured_data: Dict[str, Any]):
        """Calculate experience depth risk factor."""
        experience = structured_data.get('professional_details', {}).get('experience', [])
        if not experience:
            self.risk_factors['experience_depth'].score = 0.0
            return

        depth_indicators = []
        total_indicators = 3

        # Average experience per role
        total_description_length = 0
        for exp in experience:
            if isinstance(exp, dict):
                desc = str(exp.get('description', ''))
                total_description_length += len(desc.split())

        avg_description_length = total_description_length / len(experience) if experience else 0
        if avg_description_length >= 50:  # Detailed descriptions
            depth_indicators.append(1.0)
        elif avg_description_length >= 20:
            depth_indicators.append(0.6)

        # Experience diversity (different roles/companies)
        companies = set()
        positions = set()
        for exp in experience:
            if isinstance(exp, dict):
                company = exp.get('company', '').strip()
                position = exp.get('position', '').strip()
                if company:
                    companies.add(company.lower())
                if position:
                    positions.add(position.lower())

        diversity_score = min((len(companies) + len(positions)) / (2 * len(experience)), 1.0)
        depth_indicators.append(diversity_score)

        # Experience span (years of experience)
        # This is a simplified calculation - in practice you'd parse dates
        experience_years = len(experience) * 2  # Rough estimate: 2 years per role
        experience_score = min(experience_years / 10, 1.0)  # Cap at 10 years
        depth_indicators.append(experience_score)

        depth_score = sum(depth_indicators) / total_indicators if depth_indicators else 0
        self.risk_factors['experience_depth'].score = min(depth_score, 1.0)

    def _calculate_industry_compliance_risk(self, structured_data: Dict[str, Any],
                                           industry: Optional[str]):
        """Calculate industry compliance risk factor."""
        if not industry:
            self.risk_factors['industry_compliance'].score = 0.8  # Neutral score
            return

        compliance_indicators = []
        industry_lower = industry.lower()

        # Technology industry requirements
        if industry_lower in ['technology', 'software', 'it', 'tech']:
            # Check for technical skills
            skills = structured_data.get('professional_details', {}).get('skills', [])
            tech_keywords = ['programming', 'software', 'database', 'cloud', 'api', 'git']
            has_tech_skills = any(any(keyword in str(skill).lower() for keyword in tech_keywords)
                                for skill in skills)
            compliance_indicators.append(1.0 if has_tech_skills else 0.0)

            # Check for projects
            has_projects = bool(structured_data.get('professional_details', {}).get('projects'))
            compliance_indicators.append(1.0 if has_projects else 0.3)

        # Finance industry requirements
        elif industry_lower in ['finance', 'banking', 'financial']:
            # Check for certifications
            certs = structured_data.get('education_details', {}).get('certifications', [])
            has_finance_certs = any('cfa' in str(cert).lower() or 'cpa' in str(cert).lower()
                                  for cert in certs)
            compliance_indicators.append(1.0 if has_finance_certs else 0.4)

        # Healthcare industry requirements
        elif industry_lower in ['healthcare', 'medical', 'health']:
            # Check for licenses/certifications
            certs = structured_data.get('education_details', {}).get('certifications', [])
            license_keywords = ['license', 'certified', 'registered', 'rn', 'md']
            has_licenses = any(any(keyword in str(cert).lower() for keyword in license_keywords)
                             for cert in certs)
            compliance_indicators.append(1.0 if has_licenses else 0.0)

        else:
            # Default compliance for other industries
            compliance_indicators.append(0.8)

        compliance_score = sum(compliance_indicators) / len(compliance_indicators) if compliance_indicators else 0.7
        self.risk_factors['industry_compliance'].score = min(compliance_score, 1.0)

    def _calculate_format_consistency_risk(self, structured_data: Dict[str, Any]):
        """Calculate format consistency risk factor."""
        consistency_indicators = []
        total_indicators = 3

        # Check date format consistency in experience
        experience = structured_data.get('professional_details', {}).get('experience', [])
        date_formats = set()

        for exp in experience:
            if isinstance(exp, dict):
                for date_field in ['start_date', 'end_date']:
                    date_value = exp.get(date_field, '')
                    if date_value:
                        # Simple format detection
                        if re.match(r'\d{1,2}/\d{4}', str(date_value)):
                            date_formats.add('MM/YYYY')
                        elif re.match(r'\d{4}-\d{2}-\d{2}', str(date_value)):
                            date_formats.add('YYYY-MM-DD')
                        elif re.match(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', str(date_value)):
                            date_formats.add('Month')

        format_consistency = 1.0 if len(date_formats) <= 1 else 0.5
        consistency_indicators.append(format_consistency)

        # Check section ordering (basic heuristic)
        expected_order = ['personal_details', 'professional_summary', 'professional_details', 'education_details']
        actual_order = [k for k in expected_order if k in structured_data]
        order_score = len(actual_order) / len(expected_order)
        consistency_indicators.append(order_score)

        # Check data completeness consistency
        sections_completeness = []
        for section in ['personal_details', 'professional_details', 'education_details']:
            if section in structured_data and structured_data[section]:
                sections_completeness.append(1.0)
            else:
                sections_completeness.append(0.0)

        completeness_consistency = 1.0 - (sum(sections_completeness) / len(sections_completeness))
        consistency_indicators.append(max(0, completeness_consistency))  # Invert: more complete = more consistent

        consistency_score = sum(consistency_indicators) / total_indicators if consistency_indicators else 0.8
        self.risk_factors['format_consistency'].score = min(consistency_score, 1.0)

    def _calculate_overall_score(self) -> float:
        """Calculate weighted overall risk score."""
        weighted_sum = 0.0
        total_weight = 0.0

        for factor in self.risk_factors.values():
            weighted_sum += factor.score * factor.weight
            total_weight += factor.weight

        return (weighted_sum / total_weight) * 100 if total_weight > 0 else 0

    def _determine_risk_level(self, overall_score: float) -> RiskLevel:
        """Determine risk level based on overall score."""
        if overall_score >= 80:
            return RiskLevel.LOW
        elif overall_score >= 60:
            return RiskLevel.MEDIUM
        elif overall_score >= 40:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

    def _generate_feedback(self) -> Tuple[List[str], List[str], List[str]]:
        """Generate critical issues, warnings, and recommendations."""
        critical_issues = []
        warnings = []
        recommendations = []

        for factor in self.risk_factors.values():
            if factor.score < factor.threshold:
                if factor.score < 0.4:  # Critical threshold
                    critical_issues.append(f"{factor.name}: {factor.description} (Score: {factor.score:.1%})")
                else:
                    warnings.append(f"{factor.name}: {factor.description} (Score: {factor.score:.1%})")

            # Generate specific recommendations
            if factor.name == 'CV Completeness' and factor.score < 0.7:
                recommendations.append("Add missing sections: professional summary, detailed work experience, and education background")
            elif factor.name == 'Content Quality' and factor.score < 0.6:
                recommendations.append("Enhance content detail: expand job descriptions with specific achievements and quantify results")
            elif factor.name == 'Skills Relevance' and factor.score < 0.5:
                recommendations.append("Align skills with job requirements: add relevant technical skills and certifications")
            elif factor.name == 'Experience Depth' and factor.score < 0.6:
                recommendations.append("Strengthen experience section: add more detailed role descriptions and career progression")
            elif factor.name == 'Industry Compliance' and factor.score < 0.7:
                recommendations.append("Add industry-specific qualifications: certifications, licenses, or specialized training")
            elif factor.name == 'Format Consistency' and factor.score < 0.8:
                recommendations.append("Standardize formatting: use consistent date formats and section organization")

        return critical_issues, warnings, recommendations

    def _assess_compliance_status(self) -> Dict[str, ComplianceStatus]:
        """Assess compliance status for different criteria."""
        compliance_status = {}

        for factor in self.risk_factors.values():
            if factor.score >= 0.8:
                compliance_status[factor.name.lower().replace(' ', '_')] = ComplianceStatus.PASS
            elif factor.score >= 0.6:
                compliance_status[factor.name.lower().replace(' ', '_')] = ComplianceStatus.WARNING
            else:
                compliance_status[factor.name.lower().replace(' ', '_')] = ComplianceStatus.FAIL

        return compliance_status
